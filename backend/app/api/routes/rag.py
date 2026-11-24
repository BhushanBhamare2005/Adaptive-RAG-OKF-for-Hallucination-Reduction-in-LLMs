import time
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.modern import RAGRequest
from app.db.database import get_db
from app.db.models import Query, RetrievedChunk
from app.rag.providers import get_llm_provider
from app.rag.retriever import retrieve

router = APIRouter()


@router.get("/provider-status")
def provider_status():
    llm_provider = get_llm_provider()
    return llm_provider.health_check()


@router.post("/search")
def search_evidence(payload: RAGRequest, db: Session = Depends(get_db)):
    evidence = retrieve(db, payload.question, top_k=payload.top_k, document_ids=payload.document_ids)
    return {"query": payload.question, "results": evidence}


@router.post("/query")
async def rag_query(payload: RAGRequest, db: Session = Depends(get_db)):
    llm_provider = get_llm_provider()
    started = time.perf_counter()
    evidence = retrieve(db, payload.question, top_k=payload.top_k, document_ids=payload.document_ids)
    if not evidence:
        query = Query(
            user_question=payload.question,
            model_name=payload.model_name,
            provider_name=llm_provider.name,
            retrieval_profile={"top_k": payload.top_k, "document_ids": payload.document_ids},
            answer_text="",
            abstained=True,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
        db.add(query)
        db.commit()
        return {
            "query_id": query.id,
            "answer": "",
            "abstained": True,
            "abstention_reason": "No indexed evidence met the retrieval threshold.",
            "citations": [],
        }
    if not llm_provider.configured():
        raise HTTPException(
            status_code=503,
            detail="LLM provider is not configured. Set LLM_BASE_URL, LLM_API_KEY and LLM_MODEL.",
        )

    context_parts = []
    for index, item in enumerate(evidence, start=1):
        excerpt = item["text"]
        if len(excerpt) > 1200:
            excerpt = excerpt[:1200].rsplit(" ", 1)[0] + "..."
        context_parts.append(
            f"[{index}] {item['title']} (page {item['page_number'] or 'N/A'}): {excerpt}"
        )
    context = "\n\n".join(context_parts)
    prompt = (
        "Answer the question only from the supplied evidence. "
        "Cite claims using [n] citation markers. "
        "If the evidence is insufficient, say that it is insufficient and do not invent facts.\n\n"
        f"Question: {payload.question}\n\nEvidence:\n{context}"
    )
    try:
        answer = await llm_provider.generate(prompt, max_tokens=500)
    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=504,
            detail="The local LLM timed out while generating the answer. Try a shorter question or reduce Top-K.",
        )
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=f"The LLM provider returned an upstream error: {error.response.status_code}",
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach the configured LLM provider: {str(error)}",
        ) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    query = Query(
        user_question=payload.question,
        model_name=payload.model_name,
        provider_name=llm_provider.name,
        retrieval_profile={"top_k": payload.top_k, "document_ids": payload.document_ids},
        answer_text=answer,
        abstained=False,
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
    db.add(query)
    db.flush()
    for index, item in enumerate(evidence, start=1):
        chunk = db.get(__import__("app.db.models", fromlist=["DocumentChunk"]).DocumentChunk, item["chunk_id"])
        if chunk:
            db.add(RetrievedChunk(
                query_id=query.id,
                chunk_id=chunk.id,
                rank=index,
                similarity_score=item["similarity_score"],
                citation_label=f"[{index}]",
            ))
    db.commit()
    return {
        "query_id": query.id,
        "answer": answer,
        "abstained": False,
        "citations": [
            {
                "label": f"[{index}]",
                "chunk_id": item["chunk_id"],
                "document_id": item["document_id"],
                "title": item["title"],
                "page_number": item["page_number"],
                "section_title": item["section_title"],
                "excerpt": item["text"],
                "similarity_score": item["similarity_score"],
                "source_url": item["source_url"],
            }
            for index, item in enumerate(evidence, start=1)
        ],
    }


@router.get("/history")
def rag_history(db: Session = Depends(get_db)):
    queries = db.execute(select(Query).order_by(Query.generated_at.desc()).limit(100)).scalars().all()
    return {"queries": [{
        "id": item.id,
        "question": item.user_question,
        "answer": item.answer_text,
        "abstained": item.abstained,
        "generated_at": item.generated_at,
        "latency_ms": item.latency_ms,
    } for item in queries]}


@router.get("/history/{query_id}")
def rag_history_detail(query_id: str, db: Session = Depends(get_db)):
    query = db.get(Query, query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found.")
    return {
        "id": query.id,
        "question": query.user_question,
        "answer": query.answer_text,
        "abstained": query.abstained,
        "repair_attempted": query.repair_attempted,
        "repair_count": query.repair_count,
        "generated_at": query.generated_at,
    }
