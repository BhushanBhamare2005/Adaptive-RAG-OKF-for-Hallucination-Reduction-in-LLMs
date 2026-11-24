from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    model: Literal["baseline_rag", "self_correction", "adaptive_okf"] = "adaptive_okf"
    question: str = ""
    answer: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
