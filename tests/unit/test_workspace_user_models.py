"""Unit tests for Workspace/User models and their repositories."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User
from backend.models.workspace import Workspace
from backend.repositories.user_repository import UserRepository
from backend.repositories.workspace_repository import WorkspaceRepository

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace() -> Workspace:
    ws = Workspace()
    ws.id = uuid.uuid4()
    ws.name = "acme"
    return ws


@pytest.fixture
def user(workspace: Workspace) -> User:
    u = User()
    u.id = uuid.uuid4()
    u.workspace_id = workspace.id
    u.email = "alice@example.com"
    u.role = "admin"
    u.password_hash = "hashed"
    return u


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# Model column structure
# ---------------------------------------------------------------------------


def test_workspace_table_name():
    assert Workspace.__tablename__ == "workspaces"


def test_workspace_columns_exist():
    cols = {c.key for c in Workspace.__table__.columns}
    assert cols >= {"id", "name", "created_at", "updated_at"}


def test_user_table_name():
    assert User.__tablename__ == "users"


def test_user_columns_exist():
    cols = {c.key for c in User.__table__.columns}
    assert cols >= {
        "id",
        "workspace_id",
        "email",
        "password_hash",
        "role",
        "created_at",
        "updated_at",
    }


def test_user_email_is_unique():
    email_col = User.__table__.c.email
    assert any(
        email_col in list(constraint.columns)
        for constraint in User.__table__.constraints
        if hasattr(constraint, "columns")
    )


def test_user_workspace_fk_exists():
    fks = {fk.target_fullname for fk in User.__table__.foreign_keys}
    assert "workspaces.id" in fks


def test_workspace_repr(workspace: Workspace):
    assert "acme" in repr(workspace)


def test_user_repr(user: User):
    assert "alice@example.com" in repr(user)
    assert "admin" in repr(user)


# ---------------------------------------------------------------------------
# WorkspaceRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_workspace_repo_get(workspace: Workspace, mock_session: AsyncMock):
    mock_session.get = AsyncMock(return_value=workspace)
    repo = WorkspaceRepository(mock_session)

    result = await repo.get(workspace.id)

    mock_session.get.assert_awaited_once_with(Workspace, workspace.id)
    assert result is workspace


@pytest.mark.asyncio
async def test_workspace_repo_add(workspace: Workspace, mock_session: AsyncMock):
    mock_session.refresh = AsyncMock()
    repo = WorkspaceRepository(mock_session)

    result = await repo.add(workspace)

    mock_session.add.assert_called_once_with(workspace)
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(workspace)
    assert result is workspace


@pytest.mark.asyncio
async def test_workspace_repo_get_by_name_found(workspace: Workspace, mock_session: AsyncMock):
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = workspace
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute = AsyncMock(return_value=execute_result)

    repo = WorkspaceRepository(mock_session)
    result = await repo.get_by_name("acme")

    assert result is workspace


@pytest.mark.asyncio
async def test_workspace_repo_get_by_name_missing(mock_session: AsyncMock):
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute = AsyncMock(return_value=execute_result)

    repo = WorkspaceRepository(mock_session)
    result = await repo.get_by_name("unknown")

    assert result is None


@pytest.mark.asyncio
async def test_workspace_repo_delete(workspace: Workspace, mock_session: AsyncMock):
    repo = WorkspaceRepository(mock_session)
    await repo.delete(workspace)

    mock_session.delete.assert_called_once_with(workspace)
    mock_session.flush.assert_awaited_once()


# ---------------------------------------------------------------------------
# UserRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_user_repo_get(user: User, mock_session: AsyncMock):
    mock_session.get = AsyncMock(return_value=user)
    repo = UserRepository(mock_session)

    result = await repo.get(user.id)

    mock_session.get.assert_awaited_once_with(User, user.id)
    assert result is user


@pytest.mark.asyncio
async def test_user_repo_add(user: User, mock_session: AsyncMock):
    repo = UserRepository(mock_session)
    result = await repo.add(user)

    mock_session.add.assert_called_once_with(user)
    mock_session.flush.assert_awaited_once()
    assert result is user


@pytest.mark.asyncio
async def test_user_repo_get_by_email_found(user: User, mock_session: AsyncMock):
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = user
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute = AsyncMock(return_value=execute_result)

    repo = UserRepository(mock_session)
    result = await repo.get_by_email("alice@example.com")

    assert result is user


@pytest.mark.asyncio
async def test_user_repo_get_by_email_missing(mock_session: AsyncMock):
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute = AsyncMock(return_value=execute_result)

    repo = UserRepository(mock_session)
    result = await repo.get_by_email("nobody@example.com")

    assert result is None


@pytest.mark.asyncio
async def test_user_repo_list_by_workspace(
    user: User, workspace: Workspace, mock_session: AsyncMock
):
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [user]
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute = AsyncMock(return_value=execute_result)

    repo = UserRepository(mock_session)
    results = await repo.list_by_workspace(workspace.id)

    assert results == [user]


@pytest.mark.asyncio
async def test_user_repo_list_by_workspace_empty(workspace: Workspace, mock_session: AsyncMock):
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute = AsyncMock(return_value=execute_result)

    repo = UserRepository(mock_session)
    results = await repo.list_by_workspace(workspace.id)

    assert results == []


@pytest.mark.asyncio
async def test_user_repo_delete(user: User, mock_session: AsyncMock):
    repo = UserRepository(mock_session)
    await repo.delete(user)

    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_awaited_once()
