import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def uuidstr() -> str:
    return str(uuid.uuid4())


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    title: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str] = mapped_column(String(500), default="")
    source_type: Mapped[str] = mapped_column(String(30))
    mime_type: Mapped[str] = mapped_column(String(200), default="")
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(2048), default="")
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    language: Mapped[str] = mapped_column(String(20), default="en")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    ingested_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    versions: Mapped[list["DocumentVersion"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    document: Mapped["Document"] = relationship(back_populates="chunks")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64))
    storage_path: Mapped[str] = mapped_column(String(2048))
    diff_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    document: Mapped["Document"] = relationship(back_populates="versions")


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    user_question: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(String(100), default="")
    provider_name: Mapped[str] = mapped_column(String(100), default="")
    retrieval_profile: Mapped[dict] = mapped_column(JSON, default=dict)
    answer_text: Mapped[str] = mapped_column(Text, default="")
    generated_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    total_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    abstained: Mapped[bool] = mapped_column(Boolean, default=False)
    repair_attempted: Mapped[bool] = mapped_column(Boolean, default=False)
    repair_count: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    retrieved_chunks: Mapped[list["RetrievedChunk"]] = relationship(back_populates="query", cascade="all, delete-orphan")
    claims: Mapped[list["Claim"]] = relationship(back_populates="query", cascade="all, delete-orphan")


class RetrievedChunk(Base):
    __tablename__ = "retrieved_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("queries.id"), index=True)
    chunk_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_chunks.id"), index=True)
    rank: Mapped[int] = mapped_column(Integer)
    similarity_score: Mapped[float] = mapped_column(Float)
    rerank_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    citation_label: Mapped[str] = mapped_column(String(50))

    query: Mapped["Query"] = relationship(back_populates="retrieved_chunks")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("queries.id"), index=True)
    claim_text: Mapped[str] = mapped_column(Text)
    claim_order: Mapped[int] = mapped_column(Integer)
    classification: Mapped[str] = mapped_column(String(30), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    repair_status: Mapped[str] = mapped_column(String(30), default="none")

    query: Mapped["Query"] = relationship(back_populates="claims")


class VerificationRun(Base):
    __tablename__ = "verification_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    query_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    claim_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    engine: Mapped[str] = mapped_column(String(30))
    model_version: Mapped[str] = mapped_column(String(100), default="")
    evidence_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    source_reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    conflict_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    threshold_used: Mapped[float] = mapped_column(Float, default=0.5)
    decision: Mapped[str] = mapped_column(String(30), index=True)
    loop_number: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)


class EvidenceConflict(Base):
    __tablename__ = "evidence_conflicts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    topic_key: Mapped[str] = mapped_column(String(500))
    claim_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    document_a_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"))
    document_b_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"))
    contradiction_summary: Mapped[str] = mapped_column(Text)
    conflicting_excerpt_a: Mapped[str] = mapped_column(Text)
    conflicting_excerpt_b: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    detected_at: Mapped[datetime] = mapped_column(default=utcnow)
    resolution_status: Mapped[str] = mapped_column(String(30), default="open")
    resolved_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("queries.id"), index=True)
    claim_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(30), index=True)
    original_answer: Mapped[str] = mapped_column(Text)
    corrected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(100))
    actor: Mapped[str] = mapped_column(String(200), default="system")
    previous_value_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuidstr)
    name: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[str] = mapped_column(String(100))
    artifact_path: Mapped[str] = mapped_column(String(2048))
    feature_schema_json: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics_json: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    __table_args__ = (UniqueConstraint("name", "version", name="uq_model_name_version"),)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(200), primary_key=True)
    value_json: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
    updated_by: Mapped[str] = mapped_column(String(200), default="system")
