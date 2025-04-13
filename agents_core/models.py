from pydantic import BaseModel, Field

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