"""FastAPI auth dependencies — resolves JWT Bearer or X-API-Key to AuthContext."""

import uuid
from typing import Annotated, Optional

from fastapi import Depends, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.db import get_db
from backend.core.exceptions import ForbiddenError, UnauthorizedError
from backend.core.security import decode_access_token, hash_api_key
from backend.repositories.api_key_repository import APIKeyRepository
from backend.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False)


class AuthContext:
    """Resolved identity attached to a request after authentication."""

    __slots__ = ("user_id", "role", "workspace_id", "auth_type")

    def __init__(
        self,
        user_id: uuid.UUID,
        role: str,
        workspace_id: Optional[uuid.UUID],
        auth_type: str,
    ) -> None:
        self.user_id = user_id
        self.role = role
        self.workspace_id = workspace_id
        self.auth_type = auth_type  # "jwt" | "api_key"

    def __repr__(self) -> str:
        return (
            f"<AuthContext user_id={self.user_id} role={self.role!r} auth_type={self.auth_type!r}>"
        )


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Security(_bearer_scheme)] = None,
    x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None,
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """Resolve either a Bearer JWT or X-API-Key header into an AuthContext.

    Raises UnauthorizedError (401) when no valid credential is present.
    """
    settings = get_settings()

    # --- JWT path ---
    if credentials is not None:
        payload = decode_access_token(
            credentials.credentials,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )
        sub = payload.get("sub")
        role = payload.get("role", "member")
        ws_raw = payload.get("workspace_id")
        if not sub:
            raise UnauthorizedError("Token is missing subject claim.")
        return AuthContext(
            user_id=uuid.UUID(sub),
            role=role,
            workspace_id=uuid.UUID(ws_raw) if ws_raw else None,
            auth_type="jwt",
        )

    # --- API key path ---
    if x_api_key is not None:
        key_hash = hash_api_key(x_api_key, settings.api_key_pepper.get_secret_value())
        api_key_repo = APIKeyRepository(db)
        api_key_obj = await api_key_repo.get_by_hash(key_hash)
        if api_key_obj is None:
            raise UnauthorizedError("Invalid API key.")

        user_repo = UserRepository(db)
        user = await user_repo.get(api_key_obj.user_id)
        if user is None:
            raise UnauthorizedError("API key owner not found.")

        return AuthContext(
            user_id=user.id,
            role=user.role,
            workspace_id=user.workspace_id,
            auth_type="api_key",
        )

    raise UnauthorizedError("Authentication credentials are required.")


def require_role(*allowed_roles: str):
    """Return a FastAPI dependency that enforces role membership.

    Usage::

        @router.get("/admin-only")
        async def admin_route(auth: AuthContext = Depends(require_role("admin"))):
            ...
    """

    async def _check(
        auth: AuthContext = Depends(get_current_user),
    ) -> AuthContext:
        if auth.role not in allowed_roles:
            raise ForbiddenError(
                f"Role '{auth.role}' is not permitted. Required: {sorted(allowed_roles)}"
            )
        return auth

    return _check
