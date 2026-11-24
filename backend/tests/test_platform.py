import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.rag.chunker import chunk_sections
from app.rag.document_processor import extract_text

client = TestClient(app)


def test_ready_endpoint():
    response = client.get("/api/ready")
    assert response.status_code == 200
    body = response.json()
    assert "database" in body
    assert "llm_provider" in body


def test_document_stats_endpoint():
    response = client.get("/api/documents/stats")
    assert response.status_code == 200
    assert {"total", "indexed", "processing", "failed", "stale"} <= response.json().keys()


def test_rag_without_evidence_abstains(monkeypatch):
    import app.api.routes.rag as rag_route
    monkeypatch.setattr(rag_route, "retrieve", lambda *args, **kwargs: [])
    response = client.post("/api/rag/query", json={"question": "A unique question that has no evidence.", "top_k": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is True


def test_claim_verification_returns_records():
    response = client.post("/api/verification/answer", json={"answer": "Paris is the capital of France. It has a population."})
    assert response.status_code == 200
    assert isinstance(response.json()["claims"], list)


def test_txt_extraction_and_chunking():
    sections = extract_text("notes.txt", "text/plain", b"This is a short test document.")
    chunks = chunk_sections(sections, chunk_size=3, overlap=1)
    assert len(chunks) >= 1
    assert chunks[0]["text"]


def test_provider_config_never_returns_api_key():
    response = client.get("/api/settings/providers/config")
    assert response.status_code == 200
    body = response.json()
    assert "api_key" not in body
    assert "api_key_configured" in body


def test_provider_status_endpoint():
    response = client.get("/api/settings/providers")
    assert response.status_code == 200
    assert "llm" in response.json()


def test_website_ingestion_fetches_and_indexes_page(monkeypatch):
    from app.api.routes import documents

    page = (
        "<html><body><main><h1>Test source</h1>"
        f"<p>Unique website ingestion content {uuid.uuid4()}</p>"
        "</main></body></html>"
    ).encode()

    class MockResponse:
        status_code = 200
        headers = {"content-type": "text/html; charset=utf-8"}
        encoding = "utf-8"
        url = "https://example.com/article"

        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            yield page

    class MockStream:
        async def __aenter__(self):
            return MockResponse()

        async def __aexit__(self, *_args):
            return None

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        def stream(self, _method, _url):
            return MockStream()

    monkeypatch.setattr(documents, "validate_public_url", lambda _url: None)
    monkeypatch.setattr(documents.httpx, "AsyncClient", lambda **_kwargs: MockClient())
    monkeypatch.setattr(
        documents,
        "process_document",
        lambda db, document: (
            setattr(document, "status", "indexed"),
            db.commit(),
        ),
    )

    response = client.post(
        "/api/documents/url",
        json={"url": "example.com/article", "title": "Ingestion test"},
    )
    assert response.status_code == 200, response.text
    result = response.json()
    try:
        assert result["status"] == "indexed"
        assert result["duplicate"] is False
        assert client.get(f"/api/documents/{result['document_id']}").json()["source_url"] == "https://example.com/article"
    finally:
        client.delete(f"/api/documents/{result['document_id']}")
