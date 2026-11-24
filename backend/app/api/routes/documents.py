import hashlib
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
import ipaddress
import socket

import httpx
import trafilatura
from bs4 import BeautifulSoup
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Document, AuditEvent
from app.services.knowledge_service import list_documents, process_document, process_document_by_id
from app.services.file_storage import delete_document as delete_stored_document, store_document
from app.api.schemas.modern import URLIngestRequest

router = APIRouter()
ALLOWED = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".csv": "text/csv",
}
MAX_WEBSITE_SIZE = 10 * 1024 * 1024
MAX_REDIRECTS = 5


def normalize_public_url(url: str) -> str:
    value = url.strip()
    if not value:
        raise HTTPException(status_code=422, detail="Enter a website URL.")
    parsed = urlparse(value)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"} and "://" in value:
        raise HTTPException(status_code=422, detail="Only HTTP and HTTPS URLs are allowed.")
    if parsed.scheme.lower() not in {"http", "https"}:
        value = f"https://{value}"
    validate_public_url(value)
    return value


@router.get("/", include_in_schema=False)
@router.get("")
def get_documents(db: Session = Depends(get_db)):
    return {"documents": list_documents(db), "total": len(list_documents(db))}


@router.get("/stats")
def document_stats(db: Session = Depends(get_db)):
    documents = db.execute(select(Document)).scalars().all()
    return {
        "total": len(documents),
        "indexed": sum(document.status == "indexed" for document in documents),
        "processing": sum(document.status in {"pending", "processing"} for document in documents),
        "failed": sum(document.status == "failed" for document in documents),
        "stale": sum(document.status == "stale" for document in documents),
    }


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(status_code=422, detail=f"Unsupported file type: {suffix or 'unknown'}")
    max_size = settings.document_max_size_mb * 1024 * 1024
    data = await file.read(max_size + 1)
    if not data:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")
    if len(data) > max_size:
        raise HTTPException(status_code=413, detail=f"Documents must be smaller than {settings.document_max_size_mb} MB.")
    digest = hashlib.sha256(data).hexdigest()
    duplicate = db.execute(select(Document).where(Document.content_hash == digest)).scalar_one_or_none()
    if duplicate:
        return {"document_id": duplicate.id, "duplicate": True, "status": duplicate.status}

    safe_name = Path(file.filename or "document").name
    storage_path = store_document(f"{digest}{suffix}", data, ALLOWED[suffix])
    document = Document(
        title=Path(safe_name).stem,
        original_filename=safe_name,
        source_type="upload",
        mime_type=ALLOWED[suffix],
        storage_path=str(storage_path),
        content_hash=digest,
        status="processing",
        metadata_json={"size_bytes": len(data)},
    )
    db.add(document)
    db.flush()
    db.add(AuditEvent(event_type="document", entity_type="document", entity_id=document.id, action="uploaded"))
    db.commit()
    background_tasks.add_task(process_document_by_id, document.id)
    return {"document_id": document.id, "duplicate": False, "status": "processing"}


def validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=422, detail="Only HTTP and HTTPS URLs are allowed.")
    if parsed.username or parsed.password:
        raise HTTPException(status_code=422, detail="URLs containing usernames or passwords are not allowed.")
    host = parsed.hostname
    if not host:
        raise HTTPException(status_code=422, detail="Invalid URL.")
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        addresses = socket.getaddrinfo(host, port)
    except (socket.gaierror, ValueError) as error:
        raise HTTPException(status_code=422, detail="URL hostname could not be resolved.") from error
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address[4][0])
        except ValueError as error:
            raise HTTPException(status_code=422, detail="URL hostname resolved to an invalid address.") from error
        if not ip.is_global:
            raise HTTPException(status_code=422, detail="Private or local URLs are not allowed.")


@router.post("/url")
async def ingest_url(payload: URLIngestRequest, db: Session = Depends(get_db)):
    original_url = normalize_public_url(payload.url)
    current_url = original_url
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=False,
            headers={"User-Agent": "Adaptive-RAG-OKF/1.0", "Accept": "text/html,application/xhtml+xml,text/plain"},
        ) as client:
            for redirect_count in range(MAX_REDIRECTS + 1):
                async with client.stream("GET", current_url) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise HTTPException(status_code=502, detail="The website returned an invalid redirect.")
                        if redirect_count == MAX_REDIRECTS:
                            raise HTTPException(status_code=502, detail="The website redirected too many times.")
                        current_url = normalize_public_url(urljoin(current_url, location))
                        continue

                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                    if content_type not in {"text/html", "application/xhtml+xml", "text/plain"}:
                        raise HTTPException(
                            status_code=415,
                            detail=f"The URL must point to an HTML or text page (received {content_type or 'unknown content type'}).",
                        )
                    content_length = response.headers.get("content-length")
                    if content_length and content_length.isdigit() and int(content_length) > MAX_WEBSITE_SIZE:
                        raise HTTPException(status_code=413, detail="The website page is larger than the 10 MB limit.")

                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > MAX_WEBSITE_SIZE:
                            raise HTTPException(status_code=413, detail="The website page is larger than the 10 MB limit.")
                    page_html = bytes(body).decode(response.encoding or "utf-8", errors="replace")
                    final_url = str(response.url)
                    break
            else:
                raise HTTPException(status_code=502, detail="The website could not be reached after redirecting.")
    except httpx.TimeoutException as error:
        raise HTTPException(status_code=504, detail="The website took too long to respond.") from error
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=f"The website returned HTTP {error.response.status_code}.",
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(status_code=502, detail="Could not connect to the website. Check the URL and try again.") from error

    downloaded = page_html.strip() if content_type == "text/plain" else trafilatura.extract(
        page_html,
        include_comments=False,
        include_tables=True,
        with_metadata=True,
    )
    if not downloaded and content_type != "text/plain":
        soup = BeautifulSoup(page_html, "html.parser")
        for element in soup(["script", "style", "noscript", "svg", "nav", "footer", "form"]):
            element.decompose()
        downloaded = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
    if not downloaded:
        raise HTTPException(status_code=422, detail="No readable text could be extracted from the website.")
    data = downloaded.encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    duplicate = db.execute(select(Document).where(Document.content_hash == digest)).scalar_one_or_none()
    if duplicate:
        return {
            "document_id": duplicate.id,
            "status": duplicate.status,
            "duplicate": True,
            "error_message": duplicate.error_message,
        }
    storage_path = store_document(f"{digest}.txt", data, "text/plain")
    document = Document(
        title=payload.title.strip() or urlparse(final_url).netloc,
        original_filename=urlparse(final_url).path.rsplit("/", 1)[-1] or "website.txt",
        source_type="website",
        mime_type="text/plain",
        source_url=final_url,
        storage_path=str(storage_path),
        content_hash=digest,
        status="processing",
        metadata_json={"original_url": original_url, "final_url": final_url},
    )
    db.add(document)
    db.commit()
    process_document(db, document)
    return {
        "document_id": document.id,
        "status": document.status,
        "duplicate": False,
        "error_message": document.error_message,
    }


@router.get("/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "id": document.id,
        "title": document.title,
        "status": document.status,
        "version": document.version,
        "source_url": document.source_url,
        "content_hash": document.content_hash,
        "error_message": document.error_message,
        "metadata": document.metadata_json,
    }


@router.get("/{document_id}/chunks")
def get_chunks(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"chunks": [{
        "id": chunk.id,
        "chunk_index": chunk.chunk_index,
        "text": chunk.text,
        "page_number": chunk.page_number,
        "section_title": chunk.section_title,
        "token_count": chunk.token_count,
    } for chunk in sorted(document.chunks, key=lambda item: item.chunk_index)]}


@router.post("/{document_id}/reindex")
def reindex_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    document.status = "processing"
    document.version += 1
    db.commit()
    process_document(db, document)
    return {"document_id": document.id, "status": document.status, "version": document.version}


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    if document.storage_path:
        delete_stored_document(document.storage_path)
    db.delete(document)
    db.commit()
    return {"status": "deleted", "document_id": document_id}
