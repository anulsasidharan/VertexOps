"""Auth endpoints — JWT token issuance, registration, and API key management."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.api.dependencies.rate_limit import rate_limit
from backend.core.config import get_settings
from backend.core.db import get_db
from backend.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from backend.core.rate_limit import STRICT_POLICY
from backend.core.security import (
    create_access_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_password,
)
from backend.models.api_key import APIKey
from backend.models.user import User
from backend.models.workspace import Workspace
from backend.repositories.api_key_repository import APIKeyRepository
from backend.repositories.user_repository import UserRepository
from backend.repositories.workspace_repository import WorkspaceRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class APIKeyCreateRequest(BaseModel):
    label: Optional[str] = None


class APIKeyCreateResponse(BaseModel):
    id: uuid.UUID
    label: Optional[str]
    raw_key: str  # shown only once at creation time


class APIKeyListItem(BaseModel):
    id: uuid.UUID
    label: Optional[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account (email + password)",
    dependencies=[Depends(rate_limit(STRICT_POLICY, key_prefix="auth_register"))],
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Create a workspace, member user, and return a JWT (same shape as ``/auth/token``)."""
    settings = get_settings()
    if not settings.allow_public_signup:
        raise ForbiddenError("Public sign-up is disabled.")

    urepo = UserRepository(db)
    if await urepo.get_by_email(str(body.email)) is not None:
        raise ConflictError("An account with this email already exists.")

    ws_repo = WorkspaceRepository(db)
    ws_name = str(body.email)[:255]
    ws = Workspace(name=ws_name)
    await ws_repo.add(ws)

    user = User(
        email=str(body.email),
        password_hash=hash_password(body.password),
        role="member",
        workspace_id=ws.id,
    )
    try:
        await urepo.add(user)
    except IntegrityError as exc:
        raise ConflictError("An account with this email already exists.") from exc

    token = create_access_token(
        subject=str(user.id),
        role=user.role,
        workspace_id=user.workspace_id,
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        expires_minutes=settings.jwt_access_token_expire_minutes,
    )
    return TokenResponse(access_token=token)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Issue JWT access token",
    dependencies=[Depends(rate_limit(STRICT_POLICY, key_prefix="auth_token"))],
)
async def issue_token(
    body: TokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email + password and return a signed JWT."""
    settings = get_settings()
    repo = UserRepository(db)
    user = await repo.get_by_email(body.email)
    if user is None or not user.password_hash:
        raise UnauthorizedError("Invalid credentials.")
    if not verify_password(body.password, user.password_hash):
        raise UnauthorizedError("Invalid credentials.")

    token = create_access_token(
        subject=str(user.id),
        role=user.role,
        workspace_id=user.workspace_id,
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        expires_minutes=settings.jwt_access_token_expire_minutes,
    )
    return TokenResponse(access_token=token)


@router.post(
    "/api-keys",
    response_model=APIKeyCreateResponse,
    summary="Create API key for current user",
)
async def create_api_key(
    body: APIKeyCreateRequest,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> APIKeyCreateResponse:
    """Generate and store a new API key. The raw key is returned once only."""
    settings = get_settings()
    raw_key, _ = generate_api_key()
    key_hash = hash_api_key(raw_key, settings.api_key_pepper.get_secret_value())

    api_key = APIKey()
    api_key.id = uuid.uuid4()
    api_key.user_id = auth.user_id
    api_key.label = body.label
    api_key.key_hash = key_hash

    repo = APIKeyRepository(db)
    await repo.add(api_key)

    return APIKeyCreateResponse(id=api_key.id, label=api_key.label, raw_key=raw_key)


@router.get(
    "/api-keys",
    response_model=list[APIKeyListItem],
    summary="List API keys for current user",
)
async def list_api_keys(
    auth: Annotated[AuthContext, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> list[APIKeyListItem]:
    repo = APIKeyRepository(db)
    keys = await repo.list_by_user(auth.user_id)
    return [APIKeyListItem(id=k.id, label=k.label) for k in keys]


@router.delete(
    "/api-keys/{key_id}",
    status_code=204,
    summary="Revoke an API key",
)
async def revoke_api_key(
    key_id: uuid.UUID,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = APIKeyRepository(db)
    api_key = await repo.get(key_id)
    if api_key is None or api_key.user_id != auth.user_id:
        raise NotFoundError("API key not found.")
    await repo.delete(api_key)
