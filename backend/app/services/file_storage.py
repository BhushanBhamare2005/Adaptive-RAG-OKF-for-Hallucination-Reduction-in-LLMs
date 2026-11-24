from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import httpx

from app.core.config import settings

SUPABASE_BUCKET = "rag-documents"
REMOTE_PREFIX = f"supabase://{SUPABASE_BUCKET}/"


def _supabase_config() -> tuple[str, str] | None:
    import os

    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SECRET_KEY", "")
    return (url, key) if url and key else None


def ensure_storage_bucket() -> None:
    config = _supabase_config()
    if not config:
        if settings.database_url.startswith(("postgresql://", "postgresql+")):
            raise RuntimeError("Supabase document storage is not configured.")
        return

    url, key = config
    headers = {"Authorization": f"Bearer {key}", "apikey": key}
    response = httpx.get(
        f"{url}/storage/v1/bucket/{SUPABASE_BUCKET}",
        headers=headers,
        timeout=15.0,
    )
    if response.status_code == 200:
        return
    if response.status_code != 404:
        response.raise_for_status()

    response = httpx.post(
        f"{url}/storage/v1/bucket",
        headers=headers,
        json={"id": SUPABASE_BUCKET, "name": SUPABASE_BUCKET, "public": False},
        timeout=15.0,
    )
    response.raise_for_status()


def store_document(pathname: str, data: bytes, content_type: str) -> str:
    config = _supabase_config()
    if config:
        url, key = config
        encoded_path = quote(pathname, safe="/")
        response = httpx.post(
            f"{url}/storage/v1/object/{SUPABASE_BUCKET}/{encoded_path}",
            headers={
                "Authorization": f"Bearer {key}",
                "apikey": key,
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            content=data,
            timeout=30.0,
        )
        response.raise_for_status()
        return f"{REMOTE_PREFIX}{pathname}"

    if settings.database_url.startswith(("postgresql://", "postgresql+")):
        raise RuntimeError("Supabase document storage is not configured.")
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    destination = settings.upload_dir / Path(pathname).name
    destination.write_bytes(data)
    return str(destination)


def read_document(storage_path: str) -> bytes:
    if storage_path.startswith(REMOTE_PREFIX):
        config = _supabase_config()
        if not config:
            raise RuntimeError("Supabase document storage is not configured.")
        url, key = config
        pathname = storage_path[len(REMOTE_PREFIX):]
        encoded_path = quote(pathname, safe="/")
        response = httpx.get(
            f"{url}/storage/v1/object/{SUPABASE_BUCKET}/{encoded_path}",
            headers={"Authorization": f"Bearer {key}", "apikey": key},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.content
    return Path(storage_path).read_bytes()


def delete_document(storage_path: str) -> None:
    if storage_path.startswith(REMOTE_PREFIX):
        config = _supabase_config()
        if not config:
            raise RuntimeError("Supabase document storage is not configured.")
        url, key = config
        pathname = storage_path[len(REMOTE_PREFIX):]
        response = httpx.delete(
            f"{url}/storage/v1/object/{SUPABASE_BUCKET}",
            headers={"Authorization": f"Bearer {key}", "apikey": key},
            json={"prefixes": [pathname]},
            timeout=30.0,
        )
        response.raise_for_status()
        return
    Path(storage_path).unlink(missing_ok=True)
