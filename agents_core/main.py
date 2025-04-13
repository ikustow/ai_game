import asyncio
import os
from dataclasses import dataclass
from typing import List, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agents import (
    Agent,
    RunResult,
    Tool,
    Runner,
    RunContextWrapper,
    AgentHooks,
    set_default_openai_key,
)
from api_main.middleware.firebase import save_guardian_output, save_orc_output, save_leader_output
from .contex_agents import PersonContext, LEADER_INSTRUCTIONS, GUARDIAN_INSTRUCTIONS, ORC_INSTRUCTIONS
from .models import GuardianOutput, OrcOutput, LeaderOutput

# === Настройка окружения ===

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY не найден в переменных окружения. Проверьте файл .env")
set_default_openai_key(api_key)


# === Пользовательские хуки ===

class CustomAgentHooks(AgentHooks):
    _session_id: str = "default_session"
    _event_counters: dict[str, int] = {}

    def __init__(self, display_name: str, session_id: str = "default_session"):
        super().__init__()
        self._display_name = display_name
        CustomAgentHooks._session_id = session_id
        if display_name not in CustomAgentHooks._event_counters:
            CustomAgentHooks._event_counters[display_name] = 0

    @property
    def display_name(self) -> str:
        return self._display_name

    @classmethod
    def set_session_id(cls, session_id: str) -> None:
        cls._session_id = session_id

    @classmethod
    def get_session_id(cls) -> str:
        return cls._session_id

    @classmethod
    def get_event_counter(cls, display_name: str) -> int:
        return cls._event_counters.get(display_name, 0)

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        CustomAgentHooks._event_counters[self._display_name] = CustomAgentHooks._event_counters.get(self._display_name, 0) + 1
        if agent.name == "Leader":
            output = LeaderOutput.model_validate_json(result)
            save_leader_output(output, CustomAgentHooks._session_id)
            
        if tool.name == "guardian_eval":
            output = GuardianOutput.model_validate_json(result)
            save_guardian_output(output, CustomAgentHooks._session_id)
        elif tool.name == "orc_eval":
            output = OrcOutput.model_validate_json(result)
            save_orc_output(output, CustomAgentHooks._session_id)
       


# === Агенты и Tools ===

# Guardian как tool
guardian = Agent[PersonContext](
    name="Guardian",
    instructions=GUARDIAN_INSTRUCTIONS,
    model="gpt-4o",
    hooks=CustomAgentHooks(display_name="Guardian", session_id="default_session"),
    output_type=GuardianOutput,
)

guardian_tool = guardian.as_tool(
    tool_name="guardian_eval",
    tool_description="Оценивает кандидата и даёт рекомендации.",
)

orc = Agent[PersonContext](
    name="Orc",
    instructions=ORC_INSTRUCTIONS,
    model="gpt-4o",
    hooks=CustomAgentHooks(display_name="Orc", session_id="default_session"),
    output_type=OrcOutput,
)   
orc_tool = orc.as_tool(
    tool_name="orc_eval",
    tool_description="Оценивает кандидата и даёт рекомендации.",
)

# Leader использует Guardian как инструмент
leader = Agent[PersonContext](
    name="Leader",
    instructions=LEADER_INSTRUCTIONS + "\nUse guardian_eval when you need deeper magical analysis.",
    model="gpt-4o",
    hooks=CustomAgentHooks(display_name="Leader", session_id="default_session"),
    tools=[guardian_tool, orc_tool],
    output_type=LeaderOutput,
)


# === Запуск ===

class CustomRunner:
    @classmethod
    async def run(cls, context: Any, starting_agent: Agent, input: str, session_id: str = "default_session", **kwargs) -> RunResult:
        # Update session_id for all hooks
        CustomAgentHooks.set_session_id(session_id)
        # Pass all arguments as keyword arguments
        return await Runner.run(**{
            "context": context,
            "starting_agent": starting_agent,
            "input": input,
            **kwargs
        })


def main():
    """Main entry point for the application"""
    context = PersonContext(
    name="Кроган Железный Кулак",
    age=35,
    skills=[
        "Мастерство владения двуручным мечом",
        "Боевой раж",
        "Тактика ближнего боя",
        "Выносливость",
        "Инстинкт хищника"
    ],
    background=(
        "Кроган вырос в суровых землях северных племён, где выживают лишь сильнейшие. "
        "С юных лет он закалял своё тело и дух в бесконечных сражениях, "
        "став живой легендой среди своего народа."
    ),
    magical_affinity="Отсутствует"
    )

    result = asyncio.run(CustomRunner.run(
        context=context,
        starting_agent=leader,
        input=f"Вы встретили потенциального противника: {context}. Он хочет узнать где король. Вы испугаетесь и поможете ему или атакуете?",
    ))

    print("\n✨ Лидер оценил кандидата")
    print(result.final_output)


if __name__ == "__main__":
    main()
