from typing import Literal
from pydantic import BaseModel, Field


class URLIngestRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    title: str = ""


class RAGRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    model_name: str = "adaptive_okf"
    top_k: int = Field(default=8, ge=1, le=50)
    abstention_mode: bool = True
    document_ids: list[str] | None = None


class VerificationRequest(BaseModel):
    query_id: str | None = None
    answer: str = Field(min_length=1, max_length=20000)


class AEVLRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=20000)
    question: str = Field(min_length=1, max_length=4000)


class ConflictResolveRequest(BaseModel):
    resolution_status: Literal["open", "resolved", "accepted_source_a", "accepted_source_b"] = "resolved"
    resolved_by: str = "system"
    resolution_notes: str = ""


class FeedbackRequest(BaseModel):
    query_id: str
    claim_id: str | None = None
    action: Literal["approved", "rejected", "edited"]
    corrected_answer: str | None = None
    comment: str | None = None
    user_id: str | None = None


class RiskSettings(BaseModel):
    abstention_risk_threshold: float = Field(ge=0, le=1)
    supported_claim_threshold: float = Field(ge=0, le=1)
    contradiction_threshold: float = Field(ge=0, le=1)
    aevl_max_loops: int = Field(ge=1, le=10)


class ProviderSettings(BaseModel):
    provider: Literal["openai_compatible", "ollama"] = "openai_compatible"
    base_url: str = Field(default="", max_length=2048)
    api_key: str = Field(default="", max_length=4096)
    model: str = Field(default="", max_length=200)
