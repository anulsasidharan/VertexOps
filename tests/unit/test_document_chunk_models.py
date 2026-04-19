"""Unit tests for Document/Chunk models and their repositories."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chunk import Chunk
from backend.models.document import Document
from backend.repositories.chunk_repository import ChunkRepository
from backend.repositories.document_repository import DocumentRepository

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def document(workspace_id: uuid.UUID) -> Document:
    doc = Document()
    doc.id = uuid.uuid4()
    doc.workspace_id = workspace_id
    doc.title = "Test Doc"
    doc.format = "pdf"
    doc.content_hash = "abc123"
    doc.ingest_status = "pending"
    return doc


@pytest.fixture
def chunk(document: Document) -> Chunk:
    c = Chunk()
    c.id = uuid.uuid4()
    c.document_id = document.id
    c.chunk_index = 0
    c.text = "Hello world"
    c.token_count = 2
    c.section_path = "Introduction"
    c.vector_id = "vec-001"
    return c


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# Document model structure
# ---------------------------------------------------------------------------


def test_document_table_name():
    assert Document.__tablename__ == "documents"


def test_document_columns_exist():
    cols = {c.key for c in Document.__table__.columns}
    assert cols >= {
        "id",
        "workspace_id",
        "title",
        "source_uri",
        "format",
        "language",
        "content_hash",
        "ingest_status",
        "created_at",
        "updated_at",
    }


def test_document_metadata_column_name():
    # mapped as doc_metadata but db column is 'metadata'
    col = Document.__table__.c["metadata"]
    assert col is not None


def test_document_indexes_defined():
    index_names = {idx.name for idx in Document.__table__.indexes}
    assert "ix_documents_workspace_id" in index_names
    assert "ix_documents_content_hash" in index_names
    assert "ix_documents_ingest_status" in index_names


def test_document_workspace_fk():
    fks = {fk.target_fullname for fk in Document.__table__.foreign_keys}
    assert "workspaces.id" in fks


def test_document_repr(document: Document):
    r = repr(document)
    assert "pending" in r
    assert "Test Doc" in r


# ---------------------------------------------------------------------------
# Chunk model structure
# ---------------------------------------------------------------------------


def test_chunk_table_name():
    assert Chunk.__tablename__ == "chunks"


def test_chunk_columns_exist():
    cols = {c.key for c in Chunk.__table__.columns}
    assert cols >= {
        "id",
        "document_id",
        "chunk_index",
        "text",
        "token_count",
        "section_path",
        "vector_id",
        "created_at",
    }


def test_chunk_has_no_updated_at():
    cols = {c.key for c in Chunk.__table__.columns}
    assert "updated_at" not in cols


def test_chunk_fk_cascade():
    fk = next(fk for fk in Chunk.__table__.foreign_keys)
    assert fk.target_fullname == "documents.id"
    assert fk.ondelete == "CASCADE"


def test_chunk_indexes_defined():
    index_names = {idx.name for idx in Chunk.__table__.indexes}
    assert "ix_chunks_document_id" in index_names
    assert "ix_chunks_vector_id" in index_names


def test_chunk_repr(chunk: Chunk):
    r = repr(chunk)
    assert "0" in r  # chunk_index


# ---------------------------------------------------------------------------
# DocumentRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_document_repo_get(document: Document, mock_session: AsyncMock):
    mock_session.get = AsyncMock(return_value=document)
    repo = DocumentRepository(mock_session)

    result = await repo.get(document.id)
    mock_session.get.assert_awaited_once_with(Document, document.id)
    assert result is document


@pytest.mark.asyncio
async def test_document_repo_add(document: Document, mock_session: AsyncMock):
    repo = DocumentRepository(mock_session)
    result = await repo.add(document)

    mock_session.add.assert_called_once_with(document)
    mock_session.flush.assert_awaited_once()
    assert result is document


@pytest.mark.asyncio
async def test_document_repo_delete(document: Document, mock_session: AsyncMock):
    repo = DocumentRepository(mock_session)
    await repo.delete(document)

    mock_session.delete.assert_called_once_with(document)
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_document_repo_get_by_content_hash_found(document: Document, mock_session: AsyncMock):
    _setup_scalar_first(mock_session, document)
    repo = DocumentRepository(mock_session)

    result = await repo.get_by_content_hash("abc123")
    assert result is document


@pytest.mark.asyncio
async def test_document_repo_get_by_content_hash_missing(mock_session: AsyncMock):
    _setup_scalar_first(mock_session, None)
    repo = DocumentRepository(mock_session)

    result = await repo.get_by_content_hash("nope")
    assert result is None


@pytest.mark.asyncio
async def test_document_repo_list_by_workspace(
    document: Document, workspace_id: uuid.UUID, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [document])
    repo = DocumentRepository(mock_session)

    results = await repo.list_by_workspace(workspace_id)
    assert results == [document]


@pytest.mark.asyncio
async def test_document_repo_list_by_status(document: Document, mock_session: AsyncMock):
    _setup_scalars_all(mock_session, [document])
    repo = DocumentRepository(mock_session)

    results = await repo.list_by_status("pending")
    assert results == [document]


@pytest.mark.asyncio
async def test_document_repo_list_by_status_empty(mock_session: AsyncMock):
    _setup_scalars_all(mock_session, [])
    repo = DocumentRepository(mock_session)

    results = await repo.list_by_status("ready")
    assert results == []


@pytest.mark.asyncio
async def test_document_repo_list_by_workspace_and_status(
    document: Document, workspace_id: uuid.UUID, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [document])
    repo = DocumentRepository(mock_session)

    results = await repo.list_by_workspace_and_status(workspace_id, "pending")
    assert results == [document]


# ---------------------------------------------------------------------------
# ChunkRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chunk_repo_get(chunk: Chunk, mock_session: AsyncMock):
    mock_session.get = AsyncMock(return_value=chunk)
    repo = ChunkRepository(mock_session)

    result = await repo.get(chunk.id)
    mock_session.get.assert_awaited_once_with(Chunk, chunk.id)
    assert result is chunk


@pytest.mark.asyncio
async def test_chunk_repo_add(chunk: Chunk, mock_session: AsyncMock):
    repo = ChunkRepository(mock_session)
    result = await repo.add(chunk)

    mock_session.add.assert_called_once_with(chunk)
    mock_session.flush.assert_awaited_once()
    assert result is chunk


@pytest.mark.asyncio
async def test_chunk_repo_delete(chunk: Chunk, mock_session: AsyncMock):
    repo = ChunkRepository(mock_session)
    await repo.delete(chunk)

    mock_session.delete.assert_called_once_with(chunk)
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_chunk_repo_list_by_document(
    chunk: Chunk, document: Document, mock_session: AsyncMock
):
    _setup_scalars_all(mock_session, [chunk])
    repo = ChunkRepository(mock_session)

    results = await repo.list_by_document(document.id)
    assert results == [chunk]


@pytest.mark.asyncio
async def test_chunk_repo_list_by_document_empty(document: Document, mock_session: AsyncMock):
    _setup_scalars_all(mock_session, [])
    repo = ChunkRepository(mock_session)

    results = await repo.list_by_document(document.id)
    assert results == []


@pytest.mark.asyncio
async def test_chunk_repo_delete_by_document(document: Document, mock_session: AsyncMock):
    execute_result = MagicMock()
    execute_result.rowcount = 3
    mock_session.execute = AsyncMock(return_value=execute_result)

    repo = ChunkRepository(mock_session)
    count = await repo.delete_by_document(document.id)

    assert count == 3
    mock_session.flush.assert_awaited_once()


# ---------------------------------------------------------------------------
# Cascade relationship wiring (ORM level)
# ---------------------------------------------------------------------------


def test_document_chunks_cascade_config():
    """Document.chunks relationship must carry delete-orphan cascade."""
    rel = Document.chunks.property
    assert "delete-orphan" in rel.cascade


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_scalar_first(session: AsyncMock, value):
    scalars = MagicMock()
    scalars.first.return_value = value
    result = MagicMock()
    result.scalars.return_value = scalars
    session.execute = AsyncMock(return_value=result)


def _setup_scalars_all(session: AsyncMock, values: list):
    scalars = MagicMock()
    scalars.all.return_value = values
    result = MagicMock()
    result.scalars.return_value = scalars
    session.execute = AsyncMock(return_value=result)
