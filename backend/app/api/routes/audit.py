from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AuditEvent

router = APIRouter()


@router.get("/events")
def audit_events(db: Session = Depends(get_db)):
    events = db.execute(select(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(500)).scalars().all()
    return {"events": [{
        "id": item.id,
        "event_type": item.event_type,
        "entity_type": item.entity_type,
        "entity_id": item.entity_id,
        "action": item.action,
        "actor": item.actor,
        "timestamp": item.timestamp,
        "metadata": item.metadata_json,
    } for item in events]}
