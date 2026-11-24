from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.modern import RiskSettings, ProviderSettings
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Setting
from app.rag.providers import configure_llm_provider, get_llm_provider

router = APIRouter()


@router.get("/risk")
def get_risk_settings(db: Session = Depends(get_db)):
    values = {key: db.get(Setting, key).value_json for key in (
        "abstention_risk_threshold",
        "supported_claim_threshold",
        "contradiction_threshold",
        "aevl_max_loops",
    ) if db.get(Setting, key)}
    return {
        "abstention_risk_threshold": values.get("abstention_risk_threshold", {}).get("value", settings.abstention_risk_threshold),
        "supported_claim_threshold": values.get("supported_claim_threshold", {}).get("value", settings.supported_claim_threshold),
        "contradiction_threshold": values.get("contradiction_threshold", {}).get("value", settings.contradiction_threshold),
        "aevl_max_loops": values.get("aevl_max_loops", {}).get("value", settings.aevl_max_loops),
    }


@router.put("/risk")
def update_risk_settings(payload: RiskSettings, db: Session = Depends(get_db)):
    values = payload.model_dump()
    for key, value in values.items():
        item = db.get(Setting, key)
        if item:
            item.value_json = {"value": value}
        else:
            db.add(Setting(key=key, value_json={"value": value}, updated_by="system"))
        setattr(settings, key, value)
    db.commit()
    return values


@router.get("/providers")
def provider_settings():
    from app.rag.vector_store import VectorStoreStatus
    llm_provider = get_llm_provider()
    return {
        "llm": llm_provider.health_check(),
        "embedding": {"status": "configured", "provider": "local", "model": "hash-v1"},
        "vector_store": VectorStoreStatus.status(),
    }


@router.get("/providers/config")
def get_provider_config():
    return {
        "provider": settings.llm_provider,
        "base_url": settings.llm_base_url,
        "model": settings.llm_model,
        "api_key_configured": bool(settings.llm_api_key),
    }


@router.put("/providers")
def update_provider_config(payload: ProviderSettings, db: Session = Depends(get_db)):
    if payload.provider == "openai_compatible":
        if not payload.base_url or not payload.model:
            return {"status": "saved", "configured": False, "health": "not_configured"}
    elif not payload.model:
        return {"status": "saved", "configured": False, "health": "not_configured"}

    provider = configure_llm_provider(
        payload.provider,
        payload.base_url,
        payload.api_key,
        payload.model,
    )
    for key, value in {
        "llm_provider": payload.provider,
        "llm_base_url": payload.base_url,
        "llm_model": payload.model,
        "llm_api_key_configured": bool(payload.api_key),
    }.items():
        item = db.get(Setting, key)
        if item:
            item.value_json = {"value": value}
        else:
            db.add(Setting(key=key, value_json={"value": value}, updated_by="system"))
    db.commit()
    return {
        "status": "saved",
        "configured": provider.configured(),
        "health": provider.health_check(),
    }


@router.post("/providers/test")
async def test_provider_config(payload: ProviderSettings):
    provider = configure_llm_provider(
        payload.provider,
        payload.base_url,
        payload.api_key,
        payload.model,
    )
    if not provider.configured():
        return {"status": "not_configured", "message": "Complete the provider base URL and model."}
    try:
        answer = await provider.generate("Reply with exactly: provider connected", max_tokens=30)
        return {
            "status": "connected",
            "provider": payload.provider,
            "model": payload.model,
            "sample": answer[:200],
        }
    except Exception as error:
        return {"status": "error", "provider": payload.provider, "message": str(error)}
