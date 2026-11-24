from typing import List
from pydantic import BaseModel


class FeatureContribution(BaseModel):
    name: str
    value: float


class AnalyzeResponse(BaseModel):
    model: str
    risk_score: float
    hallucinated: bool
    features: List[FeatureContribution]
    message: str
