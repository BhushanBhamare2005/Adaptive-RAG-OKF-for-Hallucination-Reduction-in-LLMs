from __future__ import annotations

from pathlib import Path

from app.core.config import settings


class VectorStoreStatus:
    @staticmethod
    def status() -> dict:
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
