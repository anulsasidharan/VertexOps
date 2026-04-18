"""Unit tests for vector store base types and Pinecone adapter."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.vector_store.base import BaseVectorStore, SearchResult, VectorRecord


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


def test_vector_record_defaults():
    r = VectorRecord(id="v1", vector=[0.1, 0.2])
    assert r.metadata == {}
    assert r.namespace is None


def test_search_result_defaults():
    r = SearchResult(id="v1", score=0.95)
    assert r.metadata == {}


def test_base_vector_store_is_abstract():
    import inspect
    assert inspect.isabstract(BaseVectorStore)


# ---------------------------------------------------------------------------
# PineconeVectorStore — mocked
# ---------------------------------------------------------------------------


def _make_pinecone_store():
    from backend.vector_store.providers.pinecone import PineconeVectorStore
    store = PineconeVectorStore(api_key="pc-key", index_name="test-index")
    mock_index = MagicMock()
    store._index = mock_index
    return store, mock_index


@pytest.mark.asyncio
async def test_pinecone_upsert_calls_index():
    store, mock_index = _make_pinecone_store()
    records = [VectorRecord(id="1", vector=[0.1, 0.2], namespace="ns")]
    count = await store.upsert(records)
    mock_index.upsert.assert_called_once()
    assert count == 1


@pytest.mark.asyncio
async def test_pinecone_upsert_empty_returns_zero():
    store, mock_index = _make_pinecone_store()
    count = await store.upsert([])
    mock_index.upsert.assert_not_called()
    assert count == 0


@pytest.mark.asyncio
async def test_pinecone_upsert_passes_metadata():
    store, mock_index = _make_pinecone_store()
    records = [VectorRecord(id="x", vector=[0.5], metadata={"doc_id": "abc"})]
    await store.upsert(records)
    call_kwargs = mock_index.upsert.call_args[1]
    assert call_kwargs["vectors"][0]["metadata"] == {"doc_id": "abc"}


@pytest.mark.asyncio
async def test_pinecone_search_returns_results():
    store, mock_index = _make_pinecone_store()
    mock_index.query.return_value = {
        "matches": [
            {"id": "v1", "score": 0.9, "metadata": {"source": "doc1"}},
            {"id": "v2", "score": 0.7, "metadata": {}},
        ]
    }
    results = await store.search([0.1, 0.2], top_k=2)
    assert len(results) == 2
    assert results[0].id == "v1"
    assert results[0].score == 0.9
    assert results[0].metadata == {"source": "doc1"}


@pytest.mark.asyncio
async def test_pinecone_search_passes_filter():
    store, mock_index = _make_pinecone_store()
    mock_index.query.return_value = {"matches": []}
    await store.search([0.1], filter={"workspace_id": "ws1"})
    call_kwargs = mock_index.query.call_args[1]
    assert call_kwargs["filter"] == {"workspace_id": "ws1"}


@pytest.mark.asyncio
async def test_pinecone_search_no_filter_omits_key():
    store, mock_index = _make_pinecone_store()
    mock_index.query.return_value = {"matches": []}
    await store.search([0.1], filter=None)
    call_kwargs = mock_index.query.call_args[1]
    assert "filter" not in call_kwargs


@pytest.mark.asyncio
async def test_pinecone_search_empty_matches():
    store, mock_index = _make_pinecone_store()
    mock_index.query.return_value = {"matches": []}
    results = await store.search([0.1])
    assert results == []


@pytest.mark.asyncio
async def test_pinecone_delete_calls_index():
    store, mock_index = _make_pinecone_store()
    await store.delete(["v1", "v2"], namespace="ns")
    mock_index.delete.assert_called_once_with(ids=["v1", "v2"], namespace="ns")


@pytest.mark.asyncio
async def test_pinecone_delete_empty_ids_is_noop():
    store, mock_index = _make_pinecone_store()
    await store.delete([])
    mock_index.delete.assert_not_called()


@pytest.mark.asyncio
async def test_pinecone_delete_namespace():
    store, mock_index = _make_pinecone_store()
    await store.delete_namespace("my-ns")
    mock_index.delete.assert_called_once_with(delete_all=True, namespace="my-ns")


def test_pinecone_storage_uri():
    from backend.vector_store.providers.pinecone import PineconeVectorStore
    store = PineconeVectorStore(api_key="k", index_name="my-index")
    assert store._index_name == "my-index"


def test_pinecone_missing_sdk_raises():
    from backend.vector_store.providers import pinecone as pc_module

    original = pc_module._PINECONE_AVAILABLE
    try:
        with patch.dict("sys.modules", {"pinecone": None}):
            pc_module._PINECONE_AVAILABLE = None
            with pytest.raises(ImportError, match="pinecone-client"):
                pc_module._require_pinecone()
    finally:
        pc_module._PINECONE_AVAILABLE = original


# ---------------------------------------------------------------------------
# Service factory
# ---------------------------------------------------------------------------


def test_factory_returns_pinecone_when_configured():
    from backend.vector_store import service as svc_module
    from backend.vector_store.providers.pinecone import PineconeVectorStore

    svc_module._store = None
    settings = MagicMock()
    settings.pinecone_api_key = MagicMock()
    settings.pinecone_api_key.get_secret_value.return_value = "pc-test"
    settings.pinecone_index_name = "test-index"

    with patch("backend.core.config.get_settings", return_value=settings):
        store = svc_module._create_store()

    assert isinstance(store, PineconeVectorStore)
    svc_module._store = None


def test_factory_raises_when_no_provider():
    from backend.vector_store import service as svc_module

    svc_module._store = None
    settings = MagicMock()
    settings.pinecone_api_key = None
    settings.pinecone_index_name = "x"

    with patch("backend.core.config.get_settings", return_value=settings):
        with pytest.raises(RuntimeError, match="No vector store configured"):
            svc_module._create_store()
    svc_module._store = None


def test_factory_singleton():
    from backend.vector_store import service as svc_module
    from backend.vector_store.providers.pinecone import PineconeVectorStore

    svc_module._store = None
    settings = MagicMock()
    settings.pinecone_api_key = MagicMock()
    settings.pinecone_api_key.get_secret_value.return_value = "k"
    settings.pinecone_index_name = "idx"

    with patch("backend.core.config.get_settings", return_value=settings):
        a = svc_module.get_vector_store()
        b = svc_module.get_vector_store()

    assert a is b
    svc_module._store = None
