import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_candidate = Path(__file__).resolve().parents[3]
ROOT = Path("/app") if Path("/app/app").exists() else _candidate
_is_vercel = os.getenv("VERCEL") == "1"
_storage_root = Path("/tmp/adaptive-rag-okf") if _is_vercel else ROOT / "storage"
_default_llm_provider = "openai_compatible" if _is_vercel else "ollama"
_default_llm_base_url = "" if _is_vercel else "http://127.0.0.1:11434"
_default_llm_model = "" if _is_vercel else "llama3.2:1b"


def default_database_url() -> str:
    return (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL_NON_POOLING")
        or os.getenv("POSTGRES_URL")
        or f"sqlite:///{_storage_root / 'app.db'}"
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Adaptive-RAG-OKF"
    data_dir: Path = ROOT / "data"
    outputs_dir: Path = _storage_root / "outputs" if _is_vercel else ROOT / "outputs"
    model_dir: Path = _storage_root / "outputs" / "models" if _is_vercel else ROOT / "outputs" / "models"
    database_url: str = Field(default_factory=default_database_url)
    storage_dir: Path = _storage_root
    upload_dir: Path = _storage_root / "uploads"
    chroma_persist_dir: Path = _storage_root / "chroma"
    threshold: float = 0.5
    supported_claim_threshold: float = 0.70
    contradiction_threshold: float = 0.70
    abstention_risk_threshold: float = 0.75
    retrieval_top_k: int = 8
    document_max_size_mb: int = 4 if _is_vercel else 50
    aevl_max_loops: int = 3
    embedding_provider: str = "local"
    embedding_model: str = "hash-v1"
    vector_store: str = "chroma"
    llm_provider: str = _default_llm_provider
    llm_base_url: str = _default_llm_base_url
    llm_api_key: str = ""
    llm_model: str = _default_llm_model
    cors_origins: str = "http://localhost:5174"


settings = Settings()
