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

from .contex_agents import PersonContext, LEADER_INSTRUCTIONS, GUARDIAN_INSTRUCTIONS, ORC_INSTRUCTIONS


# === Настройка окружения ===

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY не найден в переменных окружения. Проверьте файл .env")
set_default_openai_key(api_key)


# === Пользовательские хуки ===

class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended tool {tool.name} with result {result}"
        )


# === Агенты и Tools ===

class GuardianOutput(BaseModel):
    joke: str = Field(description="Шутка про потенциального противника")
    attack: bool = Field(description="Атаковать или нет")
    reason: str = Field(description="Почему вы так решили, кратко и в прямой речи")

class OrcOutput(BaseModel):
    attack: bool = Field(description="Атаковать или нет, всегда да")
    reason: str = Field(description="Отвечай на орочьем языке тремя словами")

class LeaderOutput(BaseModel):
    attack: bool = Field(description="Атаковать или нет")
    reason: str = Field(description="Почему вы так решили, кратко и в прямой речи к потенциальному противнику")

# Guardian как tool
guardian = Agent[PersonContext](
    name="Guardian",
    instructions=GUARDIAN_INSTRUCTIONS,
    model="gpt-4o",
    hooks=CustomAgentHooks(display_name="Guardian"),
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
    hooks=CustomAgentHooks(display_name="Orc"),
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
    hooks=CustomAgentHooks(display_name="Leader"),
    tools=[guardian_tool, orc_tool],
    output_type=LeaderOutput,
)

# === Запуск ===

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

    result = asyncio.run(Runner.run(
        context=context,
        starting_agent=leader,
        input=f"Вы встретили потенциального противника: {context}. Он хочет узнать где король. Вы испугаетесь и поможете ему или атакуете?",
    ))

    print("\n✨ Лидер оценил кандидата")
    print(result.final_output)


if __name__ == "__main__":
    main()
