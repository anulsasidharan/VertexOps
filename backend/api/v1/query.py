"""Query API — POST /query and POST /rag/query endpoints."""

import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.core.exceptions import DomainValidationError
from backend.integrations.billing.service import record_usage_event
from backend.generation.base import GenerationRequest
from backend.generation.service import GenerationService
from backend.retrieval.base import RetrievalConfig
from backend.retrieval.service import RetrievalService

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    index_id: uuid.UUID
    top_k: int = Field(default=5, ge=1, le=50)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None
    template_name: str = "rag_default"
    max_tokens: int = Field(default=1024, ge=64, le=4096)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class SourceChunk(BaseModel):
    chunk_id: str
    document_id: str
    score: float
    text: str
    section_path: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    model: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    index_id: uuid.UUID
    top_k: int = Field(default=5, ge=1, le=50)
    context_sources: Optional[List[str]] = None
    template_name: str = "rag_default"


class RAGQueryResponse(BaseModel):
    response_text: str
    source_docs: List[SourceChunk]
    confidence_score: float
    latency_ms: float


# ---------------------------------------------------------------------------
# Dependencies (overridable in tests)
# ---------------------------------------------------------------------------


def get_retrieval_service() -> RetrievalService:
    return RetrievalService()


def get_generation_service() -> GenerationService:
    return GenerationService()


def get_embedding_service():
    from backend.embedding.service import EmbeddingService
    return EmbeddingService()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/query", response_model=QueryResponse)
async def query(
    body: QueryRequest,
    auth: AuthContext = Depends(get_current_user),
    retrieval_svc: RetrievalService = Depends(get_retrieval_service),
    generation_svc: GenerationService = Depends(get_generation_service),
    embed_svc=Depends(get_embedding_service),
) -> QueryResponse:
    """Run a RAG query: embed question → retrieve chunks → generate answer."""
    t0 = time.perf_counter()

    embedding_result = await embed_svc.embed_single(body.question)

    cfg = RetrievalConfig(
        index_id=body.index_id,
        top_k=body.top_k,
        min_score=body.min_score,
        filters=body.filters,
    )
    results = await retrieval_svc.retrieve(embedding_result, cfg)

    gen_req = GenerationRequest(
        question=body.question,
        context_chunks=[r.text for r in results],
        template_name=body.template_name,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
    )
    gen_resp = await generation_svc.generate(gen_req)

    latency_ms = (time.perf_counter() - t0) * 1000

    record_usage_event(
        "query_completion",
        float(gen_resp.total_tokens),
        metadata={
            "user_id": str(auth.user_id),
            "workspace_id": str(auth.workspace_id) if auth.workspace_id else "",
            "index_id": str(body.index_id),
            "auth_type": auth.auth_type,
        },
    )

    return QueryResponse(
        answer=gen_resp.answer,
        sources=[
            SourceChunk(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                score=r.score,
                text=r.text,
                section_path=r.section_path,
            )
            for r in results
        ],
        model=gen_resp.model,
        latency_ms=round(latency_ms, 2),
        prompt_tokens=gen_resp.prompt_tokens,
        completion_tokens=gen_resp.completion_tokens,
    )


@router.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(
    body: RAGQueryRequest,
    auth: AuthContext = Depends(get_current_user),
    retrieval_svc: RetrievalService = Depends(get_retrieval_service),
    generation_svc: GenerationService = Depends(get_generation_service),
    embed_svc=Depends(get_embedding_service),
) -> RAGQueryResponse:
    """Simplified RAG endpoint matching the legacy contract."""
    t0 = time.perf_counter()

    embedding_result = await embed_svc.embed_single(body.query)

    cfg = RetrievalConfig(index_id=body.index_id, top_k=body.top_k)
    results = await retrieval_svc.retrieve(embedding_result, cfg)

    gen_req = GenerationRequest(
        question=body.query,
        context_chunks=[r.text for r in results],
        template_name=body.template_name,
    )
    gen_resp = await generation_svc.generate(gen_req)

    confidence = max((r.score for r in results), default=0.0)
    latency_ms = (time.perf_counter() - t0) * 1000

    record_usage_event(
        "rag_query_completion",
        float(gen_resp.total_tokens),
        metadata={
            "user_id": str(auth.user_id),
            "workspace_id": str(auth.workspace_id) if auth.workspace_id else "",
            "index_id": str(body.index_id),
            "auth_type": auth.auth_type,
        },
    )

    return RAGQueryResponse(
        response_text=gen_resp.answer,
        source_docs=[
            SourceChunk(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                score=r.score,
                text=r.text,
                section_path=r.section_path,
            )
            for r in results
        ],
        confidence_score=round(confidence, 4),
        latency_ms=round(latency_ms, 2),
    )
