from __future__ import annotations

from pathlib import Path
import os

from app.core.config import settings


class VectorStoreStatus:
    @staticmethod
    def status() -> dict:
        if os.getenv("VERCEL") == "1":
            return {
                "provider": "postgresql_retrieval",
                "status": "available",
                "persist_dir": "managed database",
            }
        try:
            import chromadb  # noqa: F401
            return {
                "provider": "chroma",
                "status": "available",
                "persist_dir": str(settings.chroma_persist_dir),
            }
        except ImportError:
            return {
                "provider": "sqlite_retrieval",
                "status": "fallback",
                "persist_dir": str(settings.chroma_persist_dir),
            }


def get_collection():
    if os.getenv("VERCEL") == "1":
        return None
    try:
        import chromadb

        settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
        return client.get_or_create_collection(
            name="adaptive_rag_okf",
            metadata={"hnsw:space": "cosine"},
        )
    except Exception:
        return None
