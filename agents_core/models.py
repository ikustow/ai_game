from pydantic import BaseModel, Field

class GuardianOutput(BaseModel):
    joke: str = Field(description="Joke about the potential opponent")
    attack: bool = Field(description="Whether to attack or not")
    reason: str = Field(description="Why you made this decision, briefly and in direct speech")

class OrcOutput(BaseModel):
    attack: bool = Field(description="Whether to attack or not, always yes")
    reason: str = Field(description="Answer in orc language in three words")

class LeaderOutput(BaseModel):
    attack: bool = Field(description="Whether to attack or not")
    reason: str = Field(description="Why you made this decision, briefly and in direct speech to the potential opponent") 