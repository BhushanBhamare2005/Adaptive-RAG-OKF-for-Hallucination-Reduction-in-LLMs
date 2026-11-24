import sys
import platform
from fastapi import APIRouter

from app.core.config import settings
from app.db.database import engine
from app.rag.providers import get_llm_provider
from app.rag.vector_store import VectorStoreStatus

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "python": sys.version.split()[0],
        "platform": platform.system(),
        "models_dir": str(settings.model_dir),
    }


@router.get("/ready")
def ready():
    llm_provider = get_llm_provider()
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        database_status = "ready"
    except Exception as error:
        database_status = f"error: {error}"
    return {
        "status": "ready" if database_status == "ready" else "degraded",
        "database": database_status,
        "vector_store": VectorStoreStatus.status(),
        "embedding_provider": {
            "status": "ready",
            "provider": "local",
            "model": "hash-v1",
        },
        "llm_provider": llm_provider.health_check(),
        "models_dir": str(settings.model_dir),
    }
