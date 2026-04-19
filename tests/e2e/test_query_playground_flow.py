"""E2E: Query playground journey — RAG question answering with source citations.

Simulates an operator using the query playground:
  1. Submitting a question against an existing index.
  2. Receiving an answer with cited source chunks.
  3. Verifying latency metadata is present.
  4. Using the /rag/query alias endpoint.
  5. Confirming error handling on empty retrieval results.
  6. Confirming auth enforcement on all query endpoints.

All external dependencies (embedding, retrieval, generation) are mocked.
"""

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

_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000030")
_IDX_ID = uuid.UUID("00000000-0000-0000-0000-000000000031")


def _auth():
    return AuthContext(user_id=uuid.uuid4(), role="member", workspace_id=_WS_ID, auth_type="jwt")


def _retrieval_result(chunk_id="c1", score=0.92, text="VertexOps uses FastAPI for the API layer."):
    return RetrievalResult(
        chunk_id=chunk_id,
        document_id="doc-arch",
        workspace_id=str(_WS_ID),
        text=text,
        score=score,
        section_path="architecture/api",
    )


def _gen_response(answer="VertexOps is built on FastAPI and Google Cloud Vertex AI."):
    return GenerationResponse(
        answer=answer,
        model="gpt-4o-mini",
        prompt_tokens=120,
        completion_tokens=30,
        total_tokens=150,
    )


def _mock_embed():
    svc = MagicMock()
    svc.embed_single = AsyncMock(return_value=[0.1] * 1536)
    return svc


# ---------------------------------------------------------------------------
# Journey
# ---------------------------------------------------------------------------


class TestQueryPlaygroundJourney:
    def setup_method(self):
        self._retrieval = MagicMock()
        self._retrieval.retrieve = AsyncMock(return_value=[_retrieval_result()])
        self._generation = MagicMock()
        self._generation.generate = AsyncMock(return_value=_gen_response())

        app.dependency_overrides[get_current_user] = _auth
        app.dependency_overrides[get_retrieval_service] = lambda: self._retrieval
        app.dependency_overrides[get_generation_service] = lambda: self._generation
        app.dependency_overrides[get_embedding_service] = lambda: _mock_embed()

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_step1_query_returns_answer(self):
        """POST /query returns 200 with a non-empty answer."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/query",
                json={
                    "question": "What technology does VertexOps use for the API layer?",
                    "index_id": str(_IDX_ID),
                    "top_k": 3,
                },
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["answer"] != ""

    def test_step2_response_includes_source_chunks(self):
        """Query response contains the retrieved source chunks."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/query",
                json={
                    "question": "How does the API layer work?",
                    "index_id": str(_IDX_ID),
                },
            )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["sources"]) >= 1
        assert "chunk_id" in body["sources"][0]
        assert "score" in body["sources"][0]
        assert "text" in body["sources"][0]

    def test_step3_latency_metadata_present(self):
        """Response includes latency_ms, prompt_tokens, completion_tokens."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/query",
                json={"question": "How is VertexOps deployed?", "index_id": str(_IDX_ID)},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert "latency_ms" in body
        assert body["latency_ms"] >= 0
        assert "prompt_tokens" in body
        assert "completion_tokens" in body

    def test_step4_rag_query_alias_returns_response(self):
        """POST /rag/query alias returns equivalent structured response."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/rag/query",
                json={
                    "query": "What is VertexOps?",
                    "index_id": str(_IDX_ID),
                },
            )
        assert resp.status_code == 200
        body = resp.json()
        assert "response_text" in body
        assert "source_docs" in body

    def test_step5_empty_retrieval_still_returns_200(self):
        """When retrieval returns no results the query still succeeds gracefully."""
        self._retrieval.retrieve = AsyncMock(return_value=[])

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/query",
                json={"question": "Totally unknown topic", "index_id": str(_IDX_ID)},
            )
        assert resp.status_code == 200
        assert resp.json()["sources"] == []

    def test_step6_missing_question_field_returns_422(self):
        """Submitting a query without the required question field returns 422."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/query",
                json={"index_id": str(_IDX_ID)},
            )
        assert resp.status_code == 422

    def test_step7_unauthenticated_query_blocked(self):
        """Without credentials the query endpoint returns 401."""
        app.dependency_overrides.clear()
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/query",
                json={"question": "test", "index_id": str(_IDX_ID)},
            )
        assert resp.status_code == 401
