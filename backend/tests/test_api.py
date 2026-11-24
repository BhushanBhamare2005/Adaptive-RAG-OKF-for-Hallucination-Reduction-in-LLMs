from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "python" in body


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_datasets_summary():
    r = client.get("/api/datasets/")
    assert r.status_code == 200
    body = r.json()
    assert "total" in body
    assert "sources" in body


def test_datasets_sample():
    r = client.get("/api/datasets/sample", params={"n": 3})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_analysis_rejects_unknown_model():
    response = client.post(
        "/api/analysis/",
        json={"model": "unknown", "answer": "answer", "evidence": "evidence"},
    )
    assert response.status_code == 422


def test_training_endpoint_returns_metrics(monkeypatch):
    from app.api.routes import experiments

    metrics = {
        "adaptive_okf": {
            "accuracy": 1.0,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "roc_auc": 1.0,
        }
    }
    monkeypatch.setattr(experiments, "train_all", lambda: metrics)
    response = client.post("/api/experiments/train")

    assert response.status_code == 200
    assert response.json() == {"status": "complete", "comparison": metrics}
