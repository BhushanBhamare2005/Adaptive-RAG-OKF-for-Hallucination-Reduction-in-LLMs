import re

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Claim, Query, RetrievedChunk, VerificationRun
from app.rag.retriever import retrieve


def split_claims(answer: str) -> list[str]:
    text = re.sub(r"\s+", " ", answer.strip())
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    claims = []
    for sentence in sentences:
        if len(sentence.split()) >= 4:
            claims.append(sentence.strip())
    return claims


def token_overlap(claim: str, evidence: str) -> float:
    claim_tokens = {token for token in re.findall(r"[a-z0-9]+", claim.lower()) if len(token) > 2}
    evidence_tokens = {token for token in re.findall(r"[a-z0-9]+", evidence.lower()) if len(token) > 2}
    if not claim_tokens or not evidence_tokens:
        return 0.0
    return len(claim_tokens & evidence_tokens) / len(claim_tokens)


def classify_claim(db: Session, query_id: str, claim_text: str, order: int) -> Claim:
    evidence = retrieve(db, claim_text, top_k=settings.retrieval_top_k)
    if not evidence:
        classification = "insufficient_evidence"
        confidence = 0.0
        risk = 1.0
    else:
        scores = [token_overlap(claim_text, item["text"]) for item in evidence]
        max_score = max(scores)
        mean_similarity = sum(item["similarity_score"] for item in evidence) / len(evidence)
        if max_score >= settings.supported_claim_threshold:
            classification = "supported"
            confidence = round((max_score + max(0.0, mean_similarity)) / 2, 4)
            risk = round(1.0 - confidence, 4)
        elif max_score >= 0.35:
            classification = "contradicted"
            confidence = round(max_score, 4)
            risk = round(1.0 - max_score * 0.25, 4)
        else:
            classification = "insufficient_evidence"
            confidence = round(max_score, 4)
            risk = round(1.0 - max_score, 4)

    claim = Claim(
        query_id=query_id,
        claim_text=claim_text,
        claim_order=order,
        classification=classification,
        confidence=confidence,
        risk_score=risk,
    )
    db.add(claim)
    db.flush()
    db.add(VerificationRun(
        query_id=query_id,
        claim_id=claim.id,
        engine="adaptive_okf",
        model_version="joblib-existing",
        evidence_quality_score=confidence,
        source_reliability_score=0.5,
        conflict_score=0.0,
        risk_score=risk,
        threshold_used=settings.supported_claim_threshold,
        decision=classification,
        details_json={"retrieved_evidence_count": len(evidence), "method": "lexical_overlap"},
    ))
    db.commit()
    return claim
