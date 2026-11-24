from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas.modern import VerificationRequest
from app.db.database import get_db
from app.db.models import Claim, Query
from app.services.claim_verification_service import split_claims, classify_claim

router = APIRouter()


@router.post("/answer")
def verify_answer(payload: VerificationRequest, db: Session = Depends(get_db)):
    query = db.get(Query, payload.query_id) if payload.query_id else None
    if payload.query_id and not query:
        raise HTTPException(status_code=404, detail="Query not found.")
    if not query:
        query = Query(
            user_question="",
            answer_text=payload.answer,
            provider_name="none",
            model_name="adaptive_okf",
        )
        db.add(query)
        db.commit()
    claims = split_claims(payload.answer)
    results = [classify_claim(db, query.id, claim, index) for index, claim in enumerate(claims, start=1)]
    return {
        "query_id": query.id,
        "claims": [{
            "id": claim.id,
            "claim_text": claim.claim_text,
            "claim_order": claim.claim_order,
            "classification": claim.classification,
            "confidence": claim.confidence,
            "risk_score": claim.risk_score,
            "corrected_text": claim.corrected_text,
        } for claim in results],
    }


@router.get("/query/{query_id}")
def verify_query(query_id: str, db: Session = Depends(get_db)):
    query = db.get(Query, query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found.")
    claims = sorted(query.claims, key=lambda item: item.claim_order)
    return {"query_id": query_id, "claims": [{
        "id": claim.id,
        "claim_text": claim.claim_text,
        "classification": claim.classification,
        "confidence": claim.confidence,
        "risk_score": claim.risk_score,
        "corrected_text": claim.corrected_text,
    } for claim in claims]}
