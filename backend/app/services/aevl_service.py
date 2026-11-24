from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Query, VerificationRun
from app.services.claim_verification_service import split_claims, classify_claim


def run_aevl(db: Session, query: Query) -> dict:
    claims = split_claims(query.answer_text)
    loop_results = []
    repaired_answer = query.answer_text
    repair_count = 0

    for loop_number in range(1, settings.aevl_max_loops + 1):
        loop_claims = []
        unsupported = []
        if loop_number == 1:
            loop_claim_results = [
                classify_claim(db, query.id, claim_text, index)
                for index, claim_text in enumerate(claims, start=1)
            ]
        else:
            loop_claim_results = sorted(query.claims, key=lambda item: item.claim_order)
        for claim in loop_claim_results:
            loop_claims.append({
                "claim_id": claim.id,
                "claim_text": claim.claim_text,
                "classification": claim.classification,
                "confidence": claim.confidence,
            })
            if claim.classification in {"insufficient_evidence", "contradicted"}:
                unsupported.append(claim)

        repaired_claims = []
        if unsupported:
            for claim in unsupported:
                evidence = __import__("app.rag.retriever", fromlist=["retrieve"]).retrieve(
                    db, f"independent supporting evidence for: {claim.claim_text}",
                    top_k=settings.retrieval_top_k,
                )
                if evidence:
                    claim.repair_status = "unable_to_invent"
                    claim.corrected_text = None
                else:
                    claim.repair_status = "unresolved"
                repaired_claims.append({
                    "claim_id": claim.id,
                    "repair_status": claim.repair_status,
                    "additional_evidence_count": len(evidence),
                })
                repair_count += 1
        db.commit()

        unresolved = [item for item in loop_claims if item["classification"] != "supported"]
        loop_results.append({
            "loop": loop_number,
            "claims": loop_claims,
            "repairs": repaired_claims,
            "unresolved_count": len(unresolved),
        })
        if not unresolved:
            break

    unresolved_count = sum(1 for item in loop_results[-1]["claims"] if item["classification"] != "supported")
    abstained = unresolved_count > 0
    if abstained:
        repaired_answer = ""
    query.abstained = abstained
    query.repair_attempted = bool(loop_results)
    query.repair_count = repair_count
    db.commit()
    db.add(VerificationRun(
        query_id=query.id,
        engine="aevl",
        model_version="aevl-v1",
        evidence_quality_score=max(0.0, 1.0 - unresolved_count / max(1, len(claims))),
        source_reliability_score=0.5,
        conflict_score=0.0,
        risk_score=1.0 if abstained else 0.0,
        threshold_used=settings.abstention_risk_threshold,
        decision="abstained" if abstained else "verified",
        loop_number=len(loop_results),
        details_json={"loop_results": loop_results},
    ))
    db.commit()
    return {
        "query_id": query.id,
        "abstained": abstained,
        "original_answer": query.answer_text,
        "repaired_answer": repaired_answer,
        "repair_count": repair_count,
        "loops": loop_results,
    }
