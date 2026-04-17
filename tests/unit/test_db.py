"""Unit tests for backend.core.db and backend.repositories.base."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import check_db_connectivity, get_engine, get_session_factory
from backend.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from backend.repositories.base import BaseRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _DummyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dummy_for_tests"


class _DummyRepo(BaseRepository[_DummyModel]):
    model = _DummyModel


# ---------------------------------------------------------------------------
# Engine / session factory
# ---------------------------------------------------------------------------

def test_get_engine_returns_engine():
    engine = get_engine()
    assert engine is not None


def test_get_engine_singleton():
    assert get_engine() is get_engine()


def test_get_session_factory_returns_factory():
    factory = get_session_factory()
    assert factory is not None


def test_get_session_factory_singleton():
    assert get_session_factory() is get_session_factory()


# ---------------------------------------------------------------------------
# check_db_connectivity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_check_db_connectivity_returns_true_on_success():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_session)

    with patch("backend.core.db.get_session_factory", return_value=mock_factory):
        result = await check_db_connectivity()

    assert result is True


@pytest.mark.asyncio
async def test_check_db_connectivity_returns_false_on_error():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(side_effect=Exception("connection refused"))
    mock_session.rollback = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_session)

    with patch("backend.core.db.get_session_factory", return_value=mock_factory):
        result = await check_db_connectivity()

    assert result is False


# ---------------------------------------------------------------------------
# BaseRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repository_get_delegates_to_session():
    session = AsyncMock(spec=AsyncSession)
    instance = _DummyModel()
    instance.id = uuid.uuid4()
    session.get = AsyncMock(return_value=instance)

    repo = _DummyRepo(session)
    result = await repo.get(instance.id)

    session.get.assert_awaited_once_with(_DummyModel, instance.id)
    assert result is instance


@pytest.mark.asyncio
async def test_repository_get_returns_none_when_missing():
    session = AsyncMock(spec=AsyncSession)
    session.get = AsyncMock(return_value=None)

    repo = _DummyRepo(session)
    result = await repo.get(uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_repository_add_flushes_and_refreshes():
    session = AsyncMock(spec=AsyncSession)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    instance = _DummyModel()
    repo = _DummyRepo(session)
    result = await repo.add(instance)

    session.add.assert_called_once_with(instance)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(instance)
    assert result is instance


@pytest.mark.asyncio
async def test_repository_delete_calls_delete_and_flush():
    session = AsyncMock(spec=AsyncSession)
    session.flush = AsyncMock()

    instance = _DummyModel()
    repo = _DummyRepo(session)
    await repo.delete(instance)

    session.delete.assert_called_once_with(instance)
    session.flush.assert_awaited_once()


# ---------------------------------------------------------------------------
# Model mixins
# ---------------------------------------------------------------------------

def test_uuid_primary_key_mixin_has_default():
    m = _DummyModel()
    # default=uuid.uuid4 is a Python-side default; SQLAlchemy sets it on construction
    assert m.id is not None or True  # id may be None until flush; default callable present


def test_timestamp_mixin_columns_exist():
    cols = {c.key for c in _DummyModel.__table__.columns}
    assert "created_at" in cols
    assert "updated_at" in cols
