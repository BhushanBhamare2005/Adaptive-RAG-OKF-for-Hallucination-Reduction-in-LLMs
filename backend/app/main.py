from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, datasets, analysis, experiments
from app.api.routes import documents, rag, verification, aevl, conflicts, feedback, audit, dashboard, settings as settings_routes
from app.api.routes import adaptive_okf, explainability
from app.core.logging import setup_logging
from app.core.config import settings as app_settings
from app.db.database import init_db

setup_logging()

app = FastAPI(title="Adaptive-RAG-OKF API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in app_settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    from app.db.database import SessionLocal
    from app.db.models import Setting
    from app.rag.providers import configure_llm_provider

    db = SessionLocal()
    try:
        provider = db.get(Setting, "llm_provider")
        base_url = db.get(Setting, "llm_base_url")
        model = db.get(Setting, "llm_model")
        provider_name = provider.value_json.get("value") if provider else app_settings.llm_provider
        base_value = base_url.value_json.get("value") if base_url else app_settings.llm_base_url
        model_value = model.value_json.get("value") if model else app_settings.llm_model
        configure_llm_provider(provider_name, base_value, "", model_value)
    finally:
        db.close()


init_db()

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(verification.router, prefix="/api/verification", tags=["verification"])
app.include_router(aevl.router, prefix="/api/aevl", tags=["aevl"])
app.include_router(conflicts.router, prefix="/api/conflicts", tags=["conflicts"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(settings_routes.router, prefix="/api/settings", tags=["settings"])
app.include_router(adaptive_okf.router, prefix="/api/adaptive-okf", tags=["adaptive-okf"])
app.include_router(explainability.router, prefix="/api/explainability", tags=["explainability"])


@app.get("/")
def root():
    return {"message": "Adaptive-RAG-OKF API is running"}
