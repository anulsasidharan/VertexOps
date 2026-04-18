"""Integration tests for the async ingest-to-embed-to-index pipeline."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session():
    """Return a minimal async context manager mock for a DB session."""
    mock_begin = AsyncMock()
    mock_begin.__aenter__ = AsyncMock(return_value=None)
    mock_begin.__aexit__ = AsyncMock(return_value=False)

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=mock_begin)
    mock_session.add = MagicMock()

    mock_factory = MagicMock(return_value=mock_session)
    return mock_factory, mock_session


# ---------------------------------------------------------------------------
# _runner.run_parse_document
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_parse_document_happy_path():
    from backend.workers._runner import run_parse_document

    doc_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.doc_metadata = {"storage_key": "documents/ws/doc/file.txt", "filename": "file.txt"}
    mock_doc.ingest_status = "pending"

    mock_doc_repo = MagicMock()
    mock_doc_repo.get = AsyncMock(return_value=mock_doc)

    mock_chunk_repo = MagicMock()
    mock_chunk_repo.delete_by_document = AsyncMock(return_value=0)

    mock_storage = MagicMock()
    mock_storage.get = AsyncMock(return_value=b"Hello world. This is a test document.")

    factory, _ = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.get_storage_backend", return_value=mock_storage),
        patch("backend.workers._runner.DocumentRepository", return_value=mock_doc_repo),
        patch("backend.workers._runner.ChunkRepository", return_value=mock_chunk_repo),
    ):
        result = await run_parse_document(doc_id, ws_id)

    assert result["document_id"] == str(doc_id)
    assert result["chunk_count"] >= 1
    assert mock_doc.ingest_status == "parsed"


@pytest.mark.asyncio
async def test_run_parse_document_missing_storage_key():
    from backend.workers._runner import run_parse_document

    doc_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.doc_metadata = {}
    mock_doc.ingest_status = "pending"

    mock_doc_repo = MagicMock()
    mock_doc_repo.get = AsyncMock(return_value=mock_doc)

    factory, _ = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.DocumentRepository", return_value=mock_doc_repo),
    ):
        result = await run_parse_document(doc_id, uuid.uuid4())

    assert result["chunk_count"] == 0
    assert mock_doc.ingest_status == "failed"


@pytest.mark.asyncio
async def test_run_parse_document_not_found_raises():
    from backend.workers._runner import run_parse_document

    mock_doc_repo = MagicMock()
    mock_doc_repo.get = AsyncMock(return_value=None)

    factory, _ = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.DocumentRepository", return_value=mock_doc_repo),
    ):
        with pytest.raises(ValueError, match="not found"):
            await run_parse_document(uuid.uuid4(), uuid.uuid4())


# ---------------------------------------------------------------------------
# _runner.run_embed_document
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_embed_document_happy_path():
    from backend.workers._runner import run_embed_document
    from backend.embedding.base import EmbeddingResult

    doc_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.ingest_status = "parsed"

    chunk1 = MagicMock()
    chunk1.id = uuid.uuid4()
    chunk1.text = "chunk one text"
    chunk1.chunk_index = 0
    chunk1.section_path = None
    chunk1.vector_id = None

    mock_doc_repo = MagicMock()
    mock_doc_repo.get = AsyncMock(return_value=mock_doc)

    mock_chunk_repo = MagicMock()
    mock_chunk_repo.list_by_document = AsyncMock(return_value=[chunk1])

    mock_embed_svc = MagicMock()
    mock_embed_svc.embed_texts = AsyncMock(
        return_value=EmbeddingResult(
            embeddings=[[0.1, 0.2, 0.3]], model="test", dimensions=3
        )
    )

    mock_vector_store = MagicMock()
    mock_vector_store.upsert = AsyncMock(return_value=1)

    factory, _ = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.DocumentRepository", return_value=mock_doc_repo),
        patch("backend.workers._runner.ChunkRepository", return_value=mock_chunk_repo),
        patch("backend.workers._runner.EmbeddingService", return_value=mock_embed_svc),
        patch("backend.workers._runner.get_vector_store", return_value=mock_vector_store),
    ):
        result = await run_embed_document(doc_id, ws_id)

    assert result["document_id"] == str(doc_id)
    assert result["vector_count"] == 1
    assert mock_doc.ingest_status == "ready"
    assert chunk1.vector_id == str(chunk1.id)


@pytest.mark.asyncio
async def test_run_embed_document_no_chunks():
    from backend.workers._runner import run_embed_document

    doc_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc_repo = MagicMock()
    mock_doc_repo.get = AsyncMock(return_value=mock_doc)

    mock_chunk_repo = MagicMock()
    mock_chunk_repo.list_by_document = AsyncMock(return_value=[])

    factory, _ = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.DocumentRepository", return_value=mock_doc_repo),
        patch("backend.workers._runner.ChunkRepository", return_value=mock_chunk_repo),
    ):
        result = await run_embed_document(doc_id, uuid.uuid4())

    assert result["vector_count"] == 0
    assert mock_doc.ingest_status == "ready"


# ---------------------------------------------------------------------------
# _runner.run_build_index
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_build_index_sets_ready():
    from backend.workers._runner import run_build_index

    idx_id = uuid.uuid4()
    mock_idx = MagicMock()
    mock_idx.status = "building"

    mock_repo = MagicMock()
    mock_repo.get = AsyncMock(return_value=mock_idx)

    factory, _ = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.IndexRepository", return_value=mock_repo),
    ):
        result = await run_build_index(idx_id, uuid.uuid4())

    assert result["status"] == "ready"
    assert mock_idx.status == "ready"


@pytest.mark.asyncio
async def test_run_build_index_not_found_raises():
    from backend.workers._runner import run_build_index

    mock_repo = MagicMock()
    mock_repo.get = AsyncMock(return_value=None)

    factory, _ = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.IndexRepository", return_value=mock_repo),
    ):
        with pytest.raises(ValueError, match="not found"):
            await run_build_index(uuid.uuid4(), uuid.uuid4())


# ---------------------------------------------------------------------------
# Pipeline task — registration and routing
# ---------------------------------------------------------------------------


def test_pipeline_task_registered():
    from backend.workers.celery_app import celery_app
    from backend.workers.tasks import pipeline  # noqa: F401
    assert "backend.workers.tasks.pipeline.ingest_document" in celery_app.tasks


def test_pipeline_task_queue():
    from backend.workers.tasks.pipeline import ingest_document
    assert ingest_document.queue == "ingest"


def test_pipeline_task_max_retries():
    from backend.workers.tasks.pipeline import ingest_document
    assert ingest_document.max_retries == 3


# ---------------------------------------------------------------------------
# Retry safety — delete_by_document called before re-parse
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_parse_document_deletes_existing_chunks():
    from backend.workers._runner import run_parse_document

    doc_id = uuid.uuid4()
    mock_doc = MagicMock()
    mock_doc.doc_metadata = {"storage_key": "k/file.txt", "filename": "file.txt"}
    mock_doc.ingest_status = "pending"

    mock_doc_repo = MagicMock()
    mock_doc_repo.get = AsyncMock(return_value=mock_doc)

    mock_chunk_repo = MagicMock()
    mock_chunk_repo.delete_by_document = AsyncMock(return_value=5)

    mock_storage = MagicMock()
    mock_storage.get = AsyncMock(return_value=b"Some content to parse.")

    factory, session = _make_session()

    with (
        patch("backend.workers._runner.get_session_factory", return_value=factory),
        patch("backend.workers._runner.DocumentRepository", return_value=mock_doc_repo),
        patch("backend.workers._runner.ChunkRepository", return_value=mock_chunk_repo),
        patch("backend.workers._runner.get_storage_backend", return_value=mock_storage),
    ):
        await run_parse_document(doc_id, uuid.uuid4())

    mock_chunk_repo.delete_by_document.assert_awaited_once_with(doc_id)
