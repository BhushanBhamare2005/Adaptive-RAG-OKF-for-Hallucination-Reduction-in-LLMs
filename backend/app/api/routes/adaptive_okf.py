from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.request import AnalyzeRequest
from app.db.database import get_db
from app.db.models import VerificationRun
from app.services.prediction_service import predict
from app.core.config import settings

router = APIRouter()


@router.get("/config")
def config():
    return {
        "threshold": settings.threshold,
        "supported_claim_threshold": settings.supported_claim_threshold,
        "abstention_risk_threshold": settings.abstention_risk_threshold,
    }


@router.post("/evaluate")
def evaluate(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    result = predict(payload.model, payload.answer, payload.evidence, payload.question or "")
    risk = result.risk_score
    decision = "abstain" if risk >= settings.abstention_risk_threshold else "verified" if risk < settings.supported_claim_threshold else "review"
    run = VerificationRun(
        engine="adaptive_okf",
        model_version=payload.model,
        evidence_quality_score=sum(feature.value for feature in result.features[:2]) / 2,
        source_reliability_score=0.5,
        conflict_score=0.0,
        risk_score=risk,
        threshold_used=settings.threshold,
        decision=decision,
        details_json={"feature_values": [feature.model_dump() for feature in result.features]},
    )
    db.add(run)
    db.commit()
    return {
        "run_id": run.id,
        "risk_score": risk,
        "decision": decision,
        "threshold": settings.threshold,
        "features": [feature.model_dump() for feature in result.features],
        "message": result.message,
    }


@router.get("/runs")
def runs(db: Session = Depends(get_db)):
    items = db.execute(select(VerificationRun).where(VerificationRun.engine == "adaptive_okf").order_by(VerificationRun.created_at.desc())).scalars().all()
    return {"runs": [{
        "id": item.id,
        "model_version": item.model_version,
        "decision": item.decision,
        "risk_score": item.risk_score,
        "created_at": item.created_at,
    } for item in items]}
