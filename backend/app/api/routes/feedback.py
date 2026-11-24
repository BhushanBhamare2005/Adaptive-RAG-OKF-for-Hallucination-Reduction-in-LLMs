from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.modern import FeedbackRequest
from app.db.database import get_db
from app.db.models import Feedback, Query

router = APIRouter()


@router.post("/")
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    query = db.get(Query, payload.query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found.")
    item = Feedback(
        query_id=payload.query_id,
        claim_id=payload.claim_id,
        action=payload.action,
        original_answer=query.answer_text,
        corrected_answer=payload.corrected_answer,
        comment=payload.comment,
        user_id=payload.user_id,
    )
    db.add(item)
    db.commit()
    return {"status": "saved", "feedback_id": item.id}


@router.get("/")
def list_feedback(db: Session = Depends(get_db)):
    items = db.execute(select(Feedback).order_by(Feedback.created_at.desc())).scalars().all()
    return {"feedback": [{
        "id": item.id,
        "query_id": item.query_id,
        "claim_id": item.claim_id,
        "action": item.action,
        "original_answer": item.original_answer,
        "corrected_answer": item.corrected_answer,
        "comment": item.comment,
        "user_id": item.user_id,
        "created_at": item.created_at,
    } for item in items]}
