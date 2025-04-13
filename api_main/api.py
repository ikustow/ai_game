from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
from agents_core.main import CustomRunner
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
    session_id: str


@app.post("/evaluate-threat")
async def evaluate_threat(context_request: PersonContextRequest):
    context = PersonContext(
        name=context_request.name,
        age=context_request.age,
        skills=context_request.skills,
        background=context_request.background,
        magical_affinity=context_request.magical_affinity
    )
    
    result = await CustomRunner.run(
        context=context,
        starting_agent=leader,
        input=f"Вы встретили потенциального противника: {context}. Он хочет узнать где король. Вы испугаетесь и поможете ему или атакуете?",
        session_id=context_request.session_id
    )   

    return {"result": result.final_output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 