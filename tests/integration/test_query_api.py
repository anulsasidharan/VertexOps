"""Integration tests for the Query API endpoints."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.api.v1.query import (
    get_embedding_service,
    get_generation_service,
    get_retrieval_service,
)
from backend.generation.base import GenerationResponse
from backend.main import app
from backend.retrieval.base import RetrievalResult

_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_IDX_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")


def _auth():
    return AuthContext(user_id=uuid.uuid4(), role="member", workspace_id=_WS_ID, auth_type="jwt")


def _retrieval_result(chunk_id="c1", score=0.9):
    return RetrievalResult(
        chunk_id=chunk_id,
        document_id="doc-1",
        workspace_id=str(_WS_ID),
        text="relevant context",
        score=score,
        section_path="intro",
    )


def _gen_response(answer="The answer is 42."):
    return GenerationResponse(
        answer=answer,
        model="gpt-4o-mini",
        prompt_tokens=50,
        completion_tokens=10,
        total_tokens=60,
    )


def _mock_embed(vector=None):
    svc = MagicMock()
    svc.embed_single = AsyncMock(return_value=vector or [0.1, 0.2, 0.3])
    return svc


# ---------------------------------------------------------------------------
# POST /query — happy path
# ---------------------------------------------------------------------------


def test_query_happy_path():
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve = AsyncMock(return_value=[_retrieval_result()])
    mock_generation = MagicMock()
    mock_generation.generate = AsyncMock(return_value=_gen_response())

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_retrieval_service] = lambda: mock_retrieval
    app.dependency_overrides[get_generation_service] = lambda: mock_generation
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()

    with TestClient(app) as client:
        resp = client.post("/api/v1/query", json={
            "question": "What is the answer?",
            "index_id": str(_IDX_ID),
            "top_k": 3,
        })

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "The answer is 42."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["chunk_id"] == "c1"
    assert "latency_ms" in data
    assert "model" in data


def test_query_empty_retrieval_returns_empty_sources():
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve = AsyncMock(return_value=[])
    mock_generation = MagicMock()
    mock_generation.generate = AsyncMock(return_value=_gen_response("I don't know."))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_retrieval_service] = lambda: mock_retrieval
    app.dependency_overrides[get_generation_service] = lambda: mock_generation
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()

    with TestClient(app) as client:
        resp = client.post("/api/v1/query", json={
            "question": "Unknown question",
            "index_id": str(_IDX_ID),
        })

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["sources"] == []


def test_query_invalid_request_missing_question():
    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()
    app.dependency_overrides[get_retrieval_service] = lambda: MagicMock()
    app.dependency_overrides[get_generation_service] = lambda: MagicMock()
    with TestClient(app) as client:
        resp = client.post("/api/v1/query", json={"index_id": str(_IDX_ID)})
    app.dependency_overrides.clear()
    assert resp.status_code == 422


def test_query_invalid_request_empty_question():
    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()
    app.dependency_overrides[get_retrieval_service] = lambda: MagicMock()
    app.dependency_overrides[get_generation_service] = lambda: MagicMock()
    with TestClient(app) as client:
        resp = client.post("/api/v1/query", json={
            "question": "",
            "index_id": str(_IDX_ID),
        })
    app.dependency_overrides.clear()
    assert resp.status_code == 422


def test_query_requires_auth():
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()
    app.dependency_overrides[get_retrieval_service] = lambda: MagicMock()
    app.dependency_overrides[get_generation_service] = lambda: MagicMock()
    with TestClient(app) as client:
        resp = client.post("/api/v1/query", json={
            "question": "test",
            "index_id": str(_IDX_ID),
        })
    app.dependency_overrides.clear()
    assert resp.status_code == 401


def test_query_sources_include_section_path():
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve = AsyncMock(return_value=[
        RetrievalResult(
            chunk_id="c2", document_id="d1", workspace_id="w1",
            text="text", score=0.8, section_path="section/sub",
        )
    ])
    mock_generation = MagicMock()
    mock_generation.generate = AsyncMock(return_value=_gen_response())

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_retrieval_service] = lambda: mock_retrieval
    app.dependency_overrides[get_generation_service] = lambda: mock_generation
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()

    with TestClient(app) as client:
        resp = client.post("/api/v1/query", json={
            "question": "Q?", "index_id": str(_IDX_ID),
        })

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["sources"][0]["section_path"] == "section/sub"


# ---------------------------------------------------------------------------
# POST /rag/query
# ---------------------------------------------------------------------------


def test_rag_query_happy_path():
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve = AsyncMock(return_value=[_retrieval_result(score=0.85)])
    mock_generation = MagicMock()
    mock_generation.generate = AsyncMock(return_value=_gen_response("RAG answer"))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_retrieval_service] = lambda: mock_retrieval
    app.dependency_overrides[get_generation_service] = lambda: mock_generation
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()

    with TestClient(app) as client:
        resp = client.post("/api/v1/rag/query", json={
            "query": "Tell me about RAG",
            "index_id": str(_IDX_ID),
        })

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    data = resp.json()
    assert data["response_text"] == "RAG answer"
    assert data["confidence_score"] == 0.85
    assert len(data["source_docs"]) == 1


def test_rag_query_empty_results_zero_confidence():
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve = AsyncMock(return_value=[])
    mock_generation = MagicMock()
    mock_generation.generate = AsyncMock(return_value=_gen_response("No info"))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_retrieval_service] = lambda: mock_retrieval
    app.dependency_overrides[get_generation_service] = lambda: mock_generation
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()

    with TestClient(app) as client:
        resp = client.post("/api/v1/rag/query", json={
            "query": "Unknown",
            "index_id": str(_IDX_ID),
        })

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["confidence_score"] == 0.0


def test_rag_query_requires_auth():
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()
    app.dependency_overrides[get_retrieval_service] = lambda: MagicMock()
    app.dependency_overrides[get_generation_service] = lambda: MagicMock()
    with TestClient(app) as client:
        resp = client.post("/api/v1/rag/query", json={
            "query": "test", "index_id": str(_IDX_ID),
        })
    app.dependency_overrides.clear()
    assert resp.status_code == 401


def test_rag_query_invalid_missing_query():
    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()
    app.dependency_overrides[get_retrieval_service] = lambda: MagicMock()
    app.dependency_overrides[get_generation_service] = lambda: MagicMock()
    with TestClient(app) as client:
        resp = client.post("/api/v1/rag/query", json={"index_id": str(_IDX_ID)})
    app.dependency_overrides.clear()
    assert resp.status_code == 422
