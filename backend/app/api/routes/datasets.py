from fastapi import APIRouter, Query

from app.data.loader import load_all_datasets

router = APIRouter()


@router.get("/")
def list_datasets():
    records = load_all_datasets()
    by_source: dict[str, int] = {}
    for r in records:
        by_source[r.get("source", "unknown")] = by_source.get(r.get("source", "unknown"), 0) + 1
    return {"total": len(records), "sources": by_source}


@router.get("/sample")
def sample(n: int = Query(default=5, ge=1, le=100)):
    records = load_all_datasets()
    if not records:
        return []
    return records[:n]
