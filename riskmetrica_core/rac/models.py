from pydantic import BaseModel, Field, field_validator
from typing import List

class Context(BaseModel):
    organisation: str
    strategic_objective: str
    time_horizon_months: int = Field(ge=1, le=120)
    risk_domain: str
    category: str = "Financial"

class Dimension(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)

class RequestPayload(BaseModel):
    context: Context
    dimensions: List[Dimension]

    @field_validator('dimensions')
    @classmethod
    def at_least_one_dimension(cls, v):
        if not v:
            raise ValueError("Provide at least one dimension.")
        return v

class Contribution(BaseModel):
    name: str
    score: float
    weight: float
    contribution: float

class Result(BaseModel):
    weighted_score: float
    band: str
    statement: str
    contributions: List[Contribution]
    audit: dict
