import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Document, DocumentChunk, DocumentVersion, AuditEvent
from app.rag.chunker import chunk_sections
from app.rag.document_processor import extract_text
from app.rag.embeddings import embedding_provider
from app.rag.vector_store import get_collection


def list_documents(db: Session) -> list[dict]:
    documents = db.execute(select(Document).order_by(Document.ingested_at.desc())).scalars().all()
    return [{
        "id": item.id,
        "title": item.title,
        "original_filename": item.original_filename,
        "source_type": item.source_type,
        "mime_type": item.mime_type,
        "source_url": item.source_url,
        "status": item.status,
        "version": item.version,
        "content_hash": item.content_hash,
        "published_at": item.published_at,
        "updated_at": item.updated_at,
        "error_message": item.error_message,
    } for item in documents]


def process_document(db: Session, document: Document) -> None:
    try:
        data = Path(document.storage_path).read_bytes()
        sections = extract_text(document.original_filename or document.title, document.mime_type, data)
        chunks = chunk_sections(sections)
        for existing in list(document.chunks):
            db.delete(existing)
        db.flush()
        collection = get_collection()
        chunk_ids = []
        embeddings = []
        texts = []
        metadatas = []
        for index, chunk in enumerate(chunks):
            chunk_hash = hashlib.sha256(chunk["text"].encode("utf-8")).hexdigest()
            chunk_row = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                text=chunk["text"],
                page_number=chunk["page_number"],
                section_title=chunk["section_title"],
                token_count=chunk["token_count"],
                content_hash=chunk_hash,
            )
            db.add(chunk_row)
            db.flush()
            chunk_row.embedding_id = chunk_row.id
            chunk_ids.append(chunk_row.id)
            embeddings.append(embedding_provider.embed(chunk["text"]))
            texts.append(chunk["text"])
            metadatas.append({
                "document_id": document.id,
                "document_title": document.title,
                "page_number": str(chunk["page_number"] or ""),
                "section_title": chunk["section_title"] or "",
            })
        if collection is not None and chunk_ids:
            try:
                collection.upsert(
                    ids=chunk_ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                )
            except Exception:
                pass
        document.status = "indexed"
        document.error_message = None
        db.add(DocumentVersion(
            document_id=document.id,
            version_number=document.version,
            content_hash=document.content_hash,
            storage_path=document.storage_path,
            diff_summary="Document re-indexed",
        ))
        db.commit()
    except Exception as error:
        document.status = "failed"
        document.error_message = str(error)
        db.commit()


def process_document_by_id(document_id: str) -> None:
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        document = db.get(Document, document_id)
        if document is not None:
            process_document(db, document)
    finally:
        db.close()
