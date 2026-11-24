from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.modern import AEVLRequest
from app.db.database import get_db
from app.db.models import Query, VerificationRun
from app.services.aevl_service import run_aevl

router = APIRouter()


@router.post("/run")
def run(payload: AEVLRequest, db: Session = Depends(get_db)):
    query = Query(
        user_question=payload.question,
        answer_text=payload.answer,
        model_name="adaptive_okf",
        provider_name="none",
    )
    db.add(query)
    db.commit()
    return run_aevl(db, query)


@router.get("/runs")
def runs(db: Session = Depends(get_db)):
    items = db.execute(select(VerificationRun).where(VerificationRun.engine == "aevl").order_by(VerificationRun.created_at.desc())).scalars().all()
    return {"runs": [{
        "id": item.id,
        "query_id": item.query_id,
        "decision": item.decision,
        "risk_score": item.risk_score,
        "loop_number": item.loop_number,
        "created_at": item.created_at,
    } for item in items]}


@router.get("/runs/{run_id}")
def run_detail(run_id: str, db: Session = Depends(get_db)):
    item = db.get(VerificationRun, run_id)
    if not item:
        raise HTTPException(status_code=404, detail="AEVL run not found.")
    return {
        "id": item.id,
        "query_id": item.query_id,
        "decision": item.decision,
        "risk_score": item.risk_score,
        "loop_number": item.loop_number,
        "details": item.details_json,
        "created_at": item.created_at,
    }
