from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.modern import ConflictResolveRequest
from app.db.database import get_db
from app.db.models import EvidenceConflict, Document

router = APIRouter()


@router.get("/")
def list_conflicts(db: Session = Depends(get_db)):
    conflicts = db.execute(select(EvidenceConflict).order_by(EvidenceConflict.detected_at.desc())).scalars().all()
    return {"conflicts": [{
        "id": item.id,
        "topic_key": item.topic_key,
        "document_a_id": item.document_a_id,
        "document_b_id": item.document_b_id,
        "contradiction_summary": item.contradiction_summary,
        "excerpt_a": item.conflicting_excerpt_a,
        "excerpt_b": item.conflicting_excerpt_b,
        "severity": item.severity,
        "resolution_status": item.resolution_status,
        "detected_at": item.detected_at,
    } for item in conflicts]}


@router.post("/detect")
def detect_conflicts(db: Session = Depends(get_db)):
    from sqlalchemy import select
    from app.db.models import Document, DocumentChunk

    documents = db.execute(select(Document).where(Document.status == "indexed")).scalars().all()
    found = []
    negative_markers = ("not ", "no ", "never ", "false", "contrary", "cannot")
    for index, document_a in enumerate(documents):
        chunks_a = sorted(document_a.chunks, key=lambda item: item.chunk_index)
        for document_b in documents[index + 1:]:
            chunks_b = sorted(document_b.chunks, key=lambda item: item.chunk_index)
            for chunk_a in chunks_a[:20]:
                for chunk_b in chunks_b[:20]:
                    words_a = set(chunk_a.text.lower().split())
                    words_b = set(chunk_b.text.lower().split())
                    overlap = len(words_a & words_b) / max(1, len(words_a | words_b))
                    negative_a = any(marker in chunk_a.text.lower() for marker in negative_markers)
                    negative_b = any(marker in chunk_b.text.lower() for marker in negative_markers)
                    if overlap >= 0.20 and negative_a != negative_b:
                        existing = db.execute(select(EvidenceConflict).where(
                            EvidenceConflict.document_a_id == document_a.id,
                            EvidenceConflict.document_b_id == document_b.id,
                        ).limit(1)).scalar_one_or_none()
                        if existing:
                            continue
                        conflict = EvidenceConflict(
                            topic_key=f"{document_a.title} / {document_b.title}",
                            document_a_id=document_a.id,
                            document_b_id=document_b.id,
                            contradiction_summary="Lexical overlap with opposing negative/positive wording detected.",
                            conflicting_excerpt_a=chunk_a.text[:1000],
                            conflicting_excerpt_b=chunk_b.text[:1000],
                            severity="high" if overlap >= 0.35 else "medium",
                        )
                        db.add(conflict)
                        db.flush()
                        found.append(conflict.id)
    db.commit()
    return {"detected": len(found), "conflict_ids": found}


@router.put("/{conflict_id}/resolve")
def resolve_conflict(conflict_id: str, payload: ConflictResolveRequest, db: Session = Depends(get_db)):
    conflict = db.get(EvidenceConflict, conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found.")
    conflict.resolution_status = payload.resolution_status
    conflict.resolved_by = payload.resolved_by
    conflict.resolution_notes = payload.resolution_notes
    from datetime import datetime, timezone
    conflict.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "resolved", "conflict_id": conflict.id}
