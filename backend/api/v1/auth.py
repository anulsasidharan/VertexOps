"""Auth endpoints — JWT token issuance and API key management."""

from typing import Annotated, List, Optional
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.core.config import get_settings
from backend.core.db import get_db
from backend.core.exceptions import NotFoundError, UnauthorizedError
from backend.core.security import (
    create_access_token,
    generate_api_key,
    hash_api_key,
    verify_password,
)
from backend.models.api_key import APIKey
from backend.repositories.api_key_repository import APIKeyRepository
from backend.repositories.user_repository import UserRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class TokenRequest(BaseModel):
    email: EmailStr
    password: str


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


@router.post("/token", response_model=TokenResponse, summary="Issue JWT access token")
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
    response_model=List[APIKeyListItem],
    summary="List API keys for current user",
)
async def list_api_keys(
    auth: Annotated[AuthContext, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> List[APIKeyListItem]:
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
