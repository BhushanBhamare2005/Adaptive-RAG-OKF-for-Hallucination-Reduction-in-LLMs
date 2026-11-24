from __future__ import annotations

import math
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk
from app.rag.embeddings import embedding_provider
from app.rag.vector_store import get_collection


def cosine(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def retrieve(db: Session, query: str, top_k: int = 8, document_ids: list[str] | None = None) -> list[dict]:
    collection = get_collection()
    if collection is not None:
        try:
            query_result = collection.query(
                query_embeddings=[embedding_provider.embed(query)],
                n_results=min(top_k, max(collection.count(), 1)),
                include=["documents", "metadatas", "distances"],
            )
            ids = query_result.get("ids", [[]])[0]
            documents = query_result.get("documents", [[]])[0]
            metadatas = query_result.get("metadatas", [[]])[0]
            distances = query_result.get("distances", [[]])[0]
            chroma_results = []
            for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
                chunk = db.get(DocumentChunk, chunk_id)
                if not chunk:
                    continue
                document = db.get(Document, chunk.document_id)
                if not document or document.status != "indexed":
                    continue
                if document_ids and document.id not in document_ids:
                    continue
                chroma_results.append({
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "title": document.title,
                    "text": text,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title,
                    "source_url": document.source_url,
                    "similarity_score": round(max(0.0, 1.0 - float(distance)), 6),
                })
            if chroma_results:
                return chroma_results[:top_k]
        except Exception:
            pass
    statement = select(DocumentChunk, Document).join(Document, DocumentChunk.document_id == Document.id)
    if document_ids:
        statement = statement.where(DocumentChunk.document_id.in_(document_ids))
    statement = statement.where(Document.status == "indexed")
    rows = db.execute(statement).all()
    query_vector = embedding_provider.embed(query)
    results = []
    for chunk, document in rows:
        chunk_vector = embedding_provider.embed(chunk.text)
        score = cosine(query_vector, chunk_vector)
        results.append({
            "chunk_id": chunk.id,
            "document_id": document.id,
            "title": document.title,
            "text": chunk.text,
            "page_number": chunk.page_number,
            "section_title": chunk.section_title,
            "source_url": document.source_url,
            "similarity_score": round(score, 6),
        })
    results.sort(key=lambda item: item["similarity_score"], reverse=True)
    return results[:top_k]
