from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import asyncio
from agents import Runner
from agents_core.contex_agents import PersonContext
from agents_core.main import leader
from agents import Agent, AgentHooks, RunContextWrapper, Tool

app = FastAPI()

class PersonContextRequest(BaseModel):
    name: str
    age: int
    skills: List[str]
    background: str
    magical_affinity: str



@app.post("/evaluate-threat")
async def evaluate_threat(context_request: PersonContextRequest):
    context = PersonContext(
        name=context_request.name,
        age=context_request.age,
        skills=context_request.skills,
        background=context_request.background,
        magical_affinity=context_request.magical_affinity
    )
    
    result = await Runner.run(
        context=context,
        starting_agent=leader,
        input=f"Вы встретили потенциального противника: {context}. Он хочет узнать где король. Вы испугаетесь и поможете ему или атакуете?",
    )
    
    return {"result": result.final_output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 