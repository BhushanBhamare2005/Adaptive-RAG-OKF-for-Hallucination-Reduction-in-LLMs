from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document, DocumentChunk, Query, Claim, EvidenceConflict, Feedback, VerificationRun
from app.rag.providers import get_llm_provider

router = APIRouter()


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    llm_provider = get_llm_provider()
    documents = db.execute(select(func.count()).select_from(Document)).scalar_one()
    chunks = db.execute(select(func.count()).select_from(DocumentChunk)).scalar_one()
    queries = db.execute(select(func.count()).select_from(Query)).scalar_one()
    abstentions = db.execute(select(func.count()).select_from(Query).where(Query.abstained.is_(True))).scalar_one()
    repairs = db.execute(select(func.count()).select_from(Query).where(Query.repair_count > 0)).scalar_one()
    claims = db.execute(select(func.count()).select_from(Claim)).scalar_one()
    supported = db.execute(select(func.count()).select_from(Claim).where(Claim.classification == "supported")).scalar_one()
    conflicts = db.execute(select(func.count()).select_from(EvidenceConflict).where(EvidenceConflict.resolution_status == "open")).scalar_one()
    pending_feedback = db.execute(select(func.count()).select_from(Feedback)).scalar_one()
    average_risk = db.execute(select(func.avg(Query.total_risk_score))).scalar_one() or 0.0
    recent = db.execute(select(Query).order_by(Query.generated_at.desc()).limit(8)).scalars().all()
    runs = db.execute(select(VerificationRun).order_by(VerificationRun.created_at.desc()).limit(20)).scalars().all()
    return {
        "total_documents": documents,
        "indexed_chunks": chunks,
        "total_queries": queries,
        "abstention_percentage": round(abstentions / queries * 100, 2) if queries else 0.0,
        "successful_repair_rate": round(repairs / queries * 100, 2) if queries else 0.0,
        "verified_answer_percentage": round(supported / claims * 100, 2) if claims else 0.0,
        "hallucination_detection_rate": round((claims - supported) / claims * 100, 2) if claims else 0.0,
        "average_risk_score": round(float(average_risk), 4),
        "open_conflicts": conflicts,
        "pending_feedback": pending_feedback,
        "provider": llm_provider.health_check(),
        "recent_activity": [{
            "id": item.id,
            "question": item.user_question,
            "abstained": item.abstained,
            "risk_score": item.total_risk_score,
            "generated_at": item.generated_at,
        } for item in recent],
        "recent_verifications": [{
            "id": item.id,
            "engine": item.engine,
            "decision": item.decision,
            "risk_score": item.risk_score,
            "created_at": item.created_at,
        } for item in runs],
    }
