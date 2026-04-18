"""Cryptographic primitives for password hashing, JWT, and API key management."""

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from passlib.context import CryptContext

from backend.core.exceptions import UnauthorizedError

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_API_KEY_PREFIX = "vops_"
_API_KEY_BYTES = 32


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def create_access_token(
    subject: str,
    role: str,
    workspace_id: Optional[uuid.UUID],
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 60,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    if workspace_id is not None:
        payload["workspace_id"] = str(workspace_id)
    if extra:
        payload.update(extra)
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
) -> Dict[str, Any]:
    """Decode and validate a JWT; raises UnauthorizedError on any failure."""
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token.")


# ---------------------------------------------------------------------------
# API key generation and verification
# ---------------------------------------------------------------------------


def generate_api_key() -> tuple[str, str]:
    """Return (raw_key, hashed_key). Store only the hash; give raw to the user once."""
    raw = _API_KEY_PREFIX + secrets.token_hex(_API_KEY_BYTES)
    return raw, _hash_api_key_with_pepper(raw, pepper=None)


def hash_api_key(raw: str, pepper: str) -> str:
    """Hash a raw API key with a secret pepper (HMAC-SHA256)."""
    return _hash_api_key_with_pepper(raw, pepper)


def verify_api_key(raw: str, stored_hash: str, pepper: Optional[str] = None) -> bool:
    """Constant-time comparison of raw key against a stored HMAC hash."""
    expected = _hash_api_key_with_pepper(raw, pepper)
    return hmac.compare_digest(expected, stored_hash)


def _hash_api_key_with_pepper(raw: str, pepper: Optional[str]) -> str:
    key = pepper.encode() if pepper else b""
    return hmac.new(key, raw.encode(), hashlib.sha256).hexdigest()
