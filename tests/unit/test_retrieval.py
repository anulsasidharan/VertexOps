"""Unit tests for the retrieval service."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.retrieval.base import RetrievalConfig
from backend.retrieval.service import RetrievalService
from backend.vector_store.base import SearchResult


def _make_hit(id_: str, score: float, **meta) -> SearchResult:
    return SearchResult(id=id_, score=score, metadata=meta)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_returns_results():
    store = MagicMock()
    store.search = AsyncMock(
        return_value=[
            _make_hit(
                "chunk-1",
                0.9,
                document_id="doc-1",
                workspace_id="ws-1",
                text="hello",
                chunk_index=0,
                section_path="intro",
            )
        ]
    )
    svc = RetrievalService(vector_store=store)
    cfg = RetrievalConfig(index_id=uuid.uuid4(), top_k=5)
    results = await svc.retrieve([0.1, 0.2], cfg)

    assert len(results) == 1
    r = results[0]
    assert r.chunk_id == "chunk-1"
    assert r.document_id == "doc-1"
    assert r.score == 0.9
    assert r.section_path == "intro"
    assert r.text == "hello"


@pytest.mark.asyncio
async def test_retrieve_passes_namespace_and_filters():
    store = MagicMock()
    store.search = AsyncMock(return_value=[])
    svc = RetrievalService(vector_store=store)
    idx_id = uuid.uuid4()
    cfg = RetrievalConfig(
        index_id=idx_id,
        top_k=3,
        namespace="custom-ns",
        filters={"workspace_id": "ws-1"},
    )
    await svc.retrieve([0.0], cfg)

    store.search.assert_awaited_once_with(
        vector=[0.0],
        top_k=3,
        namespace="custom-ns",
        filter={"workspace_id": "ws-1"},
    )


@pytest.mark.asyncio
async def test_retrieve_uses_index_id_as_default_namespace():
    store = MagicMock()
    store.search = AsyncMock(return_value=[])
    svc = RetrievalService(vector_store=store)
    idx_id = uuid.uuid4()
    cfg = RetrievalConfig(index_id=idx_id, top_k=5)
    await svc.retrieve([0.0], cfg)

    _, kwargs = store.search.call_args
    assert kwargs["namespace"] == str(idx_id)


# ---------------------------------------------------------------------------
# min_score filtering
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_filters_below_min_score():
    store = MagicMock()
    store.search = AsyncMock(
        return_value=[
            _make_hit("c1", 0.8, document_id="d1", workspace_id="w1", text="a", chunk_index=0),
            _make_hit("c2", 0.3, document_id="d1", workspace_id="w1", text="b", chunk_index=1),
        ]
    )
    svc = RetrievalService(vector_store=store)
    cfg = RetrievalConfig(index_id=uuid.uuid4(), top_k=5, min_score=0.5)
    results = await svc.retrieve([0.1], cfg)

    assert len(results) == 1
    assert results[0].chunk_id == "c1"


@pytest.mark.asyncio
async def test_retrieve_empty_when_all_below_threshold():
    store = MagicMock()
    store.search = AsyncMock(
        return_value=[
            _make_hit("c1", 0.1, document_id="d", workspace_id="w", text="x", chunk_index=0)
        ]
    )
    svc = RetrievalService(vector_store=store)
    cfg = RetrievalConfig(index_id=uuid.uuid4(), top_k=5, min_score=0.9)
    results = await svc.retrieve([0.1], cfg)

    assert results == []


# ---------------------------------------------------------------------------
# Empty and error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_empty_store_result():
    store = MagicMock()
    store.search = AsyncMock(return_value=[])
    svc = RetrievalService(vector_store=store)
    cfg = RetrievalConfig(index_id=uuid.uuid4(), top_k=10)
    results = await svc.retrieve([0.0, 0.1], cfg)

    assert results == []


@pytest.mark.asyncio
async def test_retrieve_backend_failure_returns_empty():
    store = MagicMock()
    store.search = AsyncMock(side_effect=RuntimeError("pinecone unavailable"))
    svc = RetrievalService(vector_store=store)
    cfg = RetrievalConfig(index_id=uuid.uuid4(), top_k=5)
    results = await svc.retrieve([0.1], cfg)

    assert results == []


# ---------------------------------------------------------------------------
# Result ordering preserved
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_preserves_score_ordering():
    store = MagicMock()
    store.search = AsyncMock(
        return_value=[
            _make_hit("c1", 0.95, document_id="d", workspace_id="w", text="first", chunk_index=0),
            _make_hit("c2", 0.80, document_id="d", workspace_id="w", text="second", chunk_index=1),
            _make_hit("c3", 0.60, document_id="d", workspace_id="w", text="third", chunk_index=2),
        ]
    )
    svc = RetrievalService(vector_store=store)
    cfg = RetrievalConfig(index_id=uuid.uuid4(), top_k=3)
    results = await svc.retrieve([0.1], cfg)

    scores = [r.score for r in results]
    assert scores == [0.95, 0.80, 0.60]


# ---------------------------------------------------------------------------
# Metadata with missing fields defaults gracefully
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_missing_metadata_fields_default():
    store = MagicMock()
    store.search = AsyncMock(return_value=[SearchResult(id="c1", score=0.7, metadata={})])
    svc = RetrievalService(vector_store=store)
    cfg = RetrievalConfig(index_id=uuid.uuid4(), top_k=5)
    results = await svc.retrieve([0.1], cfg)

    assert len(results) == 1
    r = results[0]
    assert r.document_id == ""
    assert r.workspace_id == ""
    assert r.text == ""
    assert r.section_path is None
    assert r.chunk_index == 0
