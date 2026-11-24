import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_candidate = Path(__file__).resolve().parents[3]
ROOT = Path("/app") if Path("/app/app").exists() else _candidate


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Adaptive-RAG-OKF"
    data_dir: Path = ROOT / "data"
    outputs_dir: Path = ROOT / "outputs"
    model_dir: Path = ROOT / "outputs" / "models"
    database_url: str = f"sqlite:///{ROOT / 'storage' / 'app.db'}"
    storage_dir: Path = ROOT / "storage"
    upload_dir: Path = ROOT / "storage" / "uploads"
    chroma_persist_dir: Path = ROOT / "storage" / "chroma"
    threshold: float = 0.5
    supported_claim_threshold: float = 0.70
    contradiction_threshold: float = 0.70
    abstention_risk_threshold: float = 0.75
    retrieval_top_k: int = 8
    document_max_size_mb: int = 50
    aevl_max_loops: int = 3
    embedding_provider: str = "local"
    embedding_model: str = "hash-v1"
    vector_store: str = "chroma"
    llm_provider: str = "ollama"
    llm_base_url: str = "http://127.0.0.1:11434"
    llm_api_key: str = ""
    llm_model: str = "llama3.2:1b"
    cors_origins: str = "http://localhost:5174"


settings = Settings()
