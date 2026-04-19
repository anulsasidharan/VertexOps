"""Unit tests for security primitives, auth dependency, and RBAC role checks."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import AuthContext, get_current_user, require_role
from backend.core.exceptions import ForbiddenError, UnauthorizedError
from backend.core.security import (
    create_access_token,
    decode_access_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_api_key,
    verify_password,
)
from backend.models.api_key import APIKey
from backend.models.user import User

# ---------------------------------------------------------------------------
# Security — password hashing
# ---------------------------------------------------------------------------


def test_hash_password_returns_bcrypt_string():
    h = hash_password("mysecret")
    assert h.startswith("$2b$") or h.startswith("$2a$")


def test_verify_password_correct():
    h = hash_password("correct-horse")
    assert verify_password("correct-horse", h) is True


def test_verify_password_wrong():
    h = hash_password("correct-horse")
    assert verify_password("wrong-horse", h) is False


def test_verify_password_corrupt_hash_returns_false():
    assert verify_password("anything", "not-a-bcrypt-hash") is False


def test_hash_password_different_salts():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2


# ---------------------------------------------------------------------------
# Security — JWT
# ---------------------------------------------------------------------------

_SECRET = "test-secret-key-long-enough"
_ALGO = "HS256"


def _make_token(
    subject: str = str(uuid.uuid4()),
    role: str = "member",
    workspace_id=None,
    expires_minutes: int = 60,
) -> str:
    return create_access_token(
        subject=subject,
        role=role,
        workspace_id=workspace_id,
        secret_key=_SECRET,
        algorithm=_ALGO,
        expires_minutes=expires_minutes,
    )


def test_create_and_decode_token():
    uid = uuid.uuid4()
    ws_id = uuid.uuid4()
    token = _make_token(subject=str(uid), role="admin", workspace_id=ws_id)
    payload = decode_access_token(token, _SECRET, _ALGO)
    assert payload["sub"] == str(uid)
    assert payload["role"] == "admin"
    assert payload["workspace_id"] == str(ws_id)


def test_decode_token_no_workspace():
    token = _make_token(workspace_id=None)
    payload = decode_access_token(token, _SECRET, _ALGO)
    assert "workspace_id" not in payload


def test_decode_expired_token_raises():
    token = _make_token(expires_minutes=-1)
    with pytest.raises(UnauthorizedError, match="expired"):
        decode_access_token(token, _SECRET, _ALGO)


def test_decode_tampered_token_raises():
    token = _make_token() + "tampered"
    with pytest.raises(UnauthorizedError):
        decode_access_token(token, _SECRET, _ALGO)


def test_decode_wrong_secret_raises():
    token = _make_token()
    with pytest.raises(UnauthorizedError):
        decode_access_token(token, "wrong-secret", _ALGO)


# ---------------------------------------------------------------------------
# Security — API key
# ---------------------------------------------------------------------------


def test_generate_api_key_format():
    raw, hashed = generate_api_key()
    assert raw.startswith("vops_")
    assert len(hashed) == 64  # sha256 hex


def test_generate_api_key_unique():
    raw1, _ = generate_api_key()
    raw2, _ = generate_api_key()
    assert raw1 != raw2


def test_hash_api_key_deterministic():
    h1 = hash_api_key("vops_abc123", "pepper")
    h2 = hash_api_key("vops_abc123", "pepper")
    assert h1 == h2


def test_hash_api_key_different_pepper():
    h1 = hash_api_key("vops_abc123", "pepper1")
    h2 = hash_api_key("vops_abc123", "pepper2")
    assert h1 != h2


def test_verify_api_key_correct():
    raw = "vops_testkey"
    stored = hash_api_key(raw, "mypepper")
    assert verify_api_key(raw, stored, "mypepper") is True


def test_verify_api_key_wrong():
    stored = hash_api_key("vops_testkey", "mypepper")
    assert verify_api_key("vops_wrongkey", stored, "mypepper") is False


# ---------------------------------------------------------------------------
# AuthContext
# ---------------------------------------------------------------------------


def test_auth_context_repr():
    uid = uuid.uuid4()
    ctx = AuthContext(user_id=uid, role="admin", workspace_id=None, auth_type="jwt")
    r = repr(ctx)
    assert "admin" in r
    assert "jwt" in r


# ---------------------------------------------------------------------------
# get_current_user dependency — JWT path
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


def _make_settings_mock(secret: str = _SECRET, pepper: str = "test-pepper"):
    settings = MagicMock()
    settings.jwt_secret_key.get_secret_value.return_value = secret
    settings.jwt_algorithm = _ALGO
    settings.api_key_pepper.get_secret_value.return_value = pepper
    return settings


@pytest.mark.asyncio
async def test_get_current_user_jwt_success(mock_db: AsyncMock):
    uid = uuid.uuid4()
    ws_id = uuid.uuid4()
    token = _make_token(subject=str(uid), role="admin", workspace_id=ws_id)

    mock_credentials = MagicMock()
    mock_credentials.credentials = token

    with patch(
        "backend.api.dependencies.auth.get_settings",
        return_value=_make_settings_mock(),
    ):
        ctx = await get_current_user(credentials=mock_credentials, x_api_key=None, db=mock_db)

    assert ctx.user_id == uid
    assert ctx.role == "admin"
    assert ctx.workspace_id == ws_id
    assert ctx.auth_type == "jwt"


@pytest.mark.asyncio
async def test_get_current_user_jwt_expired(mock_db: AsyncMock):
    token = _make_token(expires_minutes=-1)
    mock_credentials = MagicMock()
    mock_credentials.credentials = token

    with patch(
        "backend.api.dependencies.auth.get_settings",
        return_value=_make_settings_mock(),
    ):
        with pytest.raises(UnauthorizedError, match="expired"):
            await get_current_user(credentials=mock_credentials, x_api_key=None, db=mock_db)


@pytest.mark.asyncio
async def test_get_current_user_no_credentials_raises(mock_db: AsyncMock):
    with pytest.raises(UnauthorizedError, match="required"):
        await get_current_user(credentials=None, x_api_key=None, db=mock_db)


# ---------------------------------------------------------------------------
# get_current_user dependency — API key path
# ---------------------------------------------------------------------------


def _make_api_key_fixture(user_id: uuid.UUID) -> APIKey:
    ak = APIKey()
    ak.id = uuid.uuid4()
    ak.user_id = user_id
    ak.label = "test-key"
    ak.key_hash = "dummy"
    return ak


def _make_user_fixture(user_id: uuid.UUID, role: str = "member") -> User:
    u = User()
    u.id = user_id
    u.email = "test@example.com"
    u.role = role
    u.workspace_id = None
    return u


@pytest.mark.asyncio
async def test_get_current_user_api_key_success(mock_db: AsyncMock):
    uid = uuid.uuid4()
    raw_key = "vops_testrawkey"
    pepper = "test-pepper"
    stored_hash = hash_api_key(raw_key, pepper)

    api_key_obj = _make_api_key_fixture(uid)
    api_key_obj.key_hash = stored_hash
    user_obj = _make_user_fixture(uid, role="member")

    settings_mock = _make_settings_mock(pepper=pepper)

    with (
        patch("backend.api.dependencies.auth.get_settings", return_value=settings_mock),
        patch("backend.api.dependencies.auth.APIKeyRepository") as MockAPIKeyRepo,
        patch("backend.api.dependencies.auth.UserRepository") as MockUserRepo,
    ):
        MockAPIKeyRepo.return_value.get_by_hash = AsyncMock(return_value=api_key_obj)
        MockUserRepo.return_value.get = AsyncMock(return_value=user_obj)

        ctx = await get_current_user(credentials=None, x_api_key=raw_key, db=mock_db)

    assert ctx.user_id == uid
    assert ctx.role == "member"
    assert ctx.auth_type == "api_key"


@pytest.mark.asyncio
async def test_get_current_user_invalid_api_key_raises(mock_db: AsyncMock):
    settings_mock = _make_settings_mock()

    with (
        patch("backend.api.dependencies.auth.get_settings", return_value=settings_mock),
        patch("backend.api.dependencies.auth.APIKeyRepository") as MockAPIKeyRepo,
    ):
        MockAPIKeyRepo.return_value.get_by_hash = AsyncMock(return_value=None)

        with pytest.raises(UnauthorizedError, match="Invalid API key"):
            await get_current_user(credentials=None, x_api_key="vops_bad_key", db=mock_db)


@pytest.mark.asyncio
async def test_get_current_user_api_key_user_not_found_raises(mock_db: AsyncMock):
    uid = uuid.uuid4()
    raw_key = "vops_testrawkey"
    pepper = "test-pepper"
    stored_hash = hash_api_key(raw_key, pepper)

    api_key_obj = _make_api_key_fixture(uid)
    api_key_obj.key_hash = stored_hash
    settings_mock = _make_settings_mock(pepper=pepper)

    with (
        patch("backend.api.dependencies.auth.get_settings", return_value=settings_mock),
        patch("backend.api.dependencies.auth.APIKeyRepository") as MockAPIKeyRepo,
        patch("backend.api.dependencies.auth.UserRepository") as MockUserRepo,
    ):
        MockAPIKeyRepo.return_value.get_by_hash = AsyncMock(return_value=api_key_obj)
        MockUserRepo.return_value.get = AsyncMock(return_value=None)

        with pytest.raises(UnauthorizedError, match="owner not found"):
            await get_current_user(credentials=None, x_api_key=raw_key, db=mock_db)


# ---------------------------------------------------------------------------
# require_role RBAC checks
# ---------------------------------------------------------------------------


def _make_auth_context(role: str) -> AuthContext:
    return AuthContext(
        user_id=uuid.uuid4(),
        role=role,
        workspace_id=None,
        auth_type="jwt",
    )


@pytest.mark.asyncio
async def test_require_role_admin_allowed():
    ctx = _make_auth_context("admin")
    checker = require_role("admin", "member")
    result = await checker(auth=ctx)
    assert result is ctx


@pytest.mark.asyncio
async def test_require_role_member_allowed():
    ctx = _make_auth_context("member")
    checker = require_role("admin", "member")
    result = await checker(auth=ctx)
    assert result is ctx


@pytest.mark.asyncio
async def test_require_role_forbidden():
    ctx = _make_auth_context("member")
    checker = require_role("admin")
    with pytest.raises(ForbiddenError):
        await checker(auth=ctx)


@pytest.mark.asyncio
async def test_require_role_api_context_allowed():
    ctx = _make_auth_context("api")
    checker = require_role("api", "admin")
    result = await checker(auth=ctx)
    assert result is ctx


# ---------------------------------------------------------------------------
# APIKey model structure
# ---------------------------------------------------------------------------


def test_api_key_table_name():
    assert APIKey.__tablename__ == "api_keys"


def test_api_key_columns_exist():
    cols = {c.key for c in APIKey.__table__.columns}
    assert cols >= {"id", "user_id", "label", "key_hash", "created_at", "last_used_at"}


def test_api_key_key_hash_unique():
    col = APIKey.__table__.c["key_hash"]
    assert any(col is c for c in col.table.constraints or []) or col.unique


def test_api_key_user_fk_cascade():
    fk = next(fk for fk in APIKey.__table__.foreign_keys)
    assert fk.target_fullname == "users.id"
    assert fk.ondelete == "CASCADE"


def test_api_key_indexes_defined():
    names = {idx.name for idx in APIKey.__table__.indexes}
    assert "ix_api_keys_user_id" in names
    assert "ix_api_keys_key_hash" in names


def test_api_key_repr():
    ak = APIKey()
    ak.id = uuid.uuid4()
    ak.label = "my-key"
    r = repr(ak)
    assert "my-key" in r


def test_user_api_keys_relationship_cascade():
    rel = User.api_keys.property
    assert "delete-orphan" in rel.cascade
