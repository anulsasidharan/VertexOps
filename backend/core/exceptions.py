"""Domain exception hierarchy and error envelope schema."""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Error codes — align with API_SPEC.md §1.2
# ---------------------------------------------------------------------------

class ErrorCode(str, Enum):
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# ---------------------------------------------------------------------------
# Error envelope — the JSON shape returned on all error responses
# ---------------------------------------------------------------------------

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = {}


class ErrorEnvelope(BaseModel):
    error: ErrorDetail

    @classmethod
    def build(
        cls,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> "ErrorEnvelope":
        return cls(error=ErrorDetail(code=code, message=message, details=details or {}))


# ---------------------------------------------------------------------------
# Domain exception base
# ---------------------------------------------------------------------------

class VertexOpsError(Exception):
    """Base for all domain-level errors.

    Subclasses declare a default ``status_code`` and ``error_code`` so the
    exception handler can produce the right HTTP response without any
    isinstance ladder.
    """

    status_code: int = 500
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details: Dict[str, Any] = details or {}

    def to_envelope(self) -> ErrorEnvelope:
        return ErrorEnvelope.build(self.error_code, self.message, self.details)


# ---------------------------------------------------------------------------
# Concrete domain exceptions
# ---------------------------------------------------------------------------

class NotFoundError(VertexOpsError):
    status_code = 404
    error_code = ErrorCode.NOT_FOUND

    def __init__(self, message: str = "Resource not found.", **kw: Any) -> None:
        super().__init__(message, **kw)


class ForbiddenError(VertexOpsError):
    status_code = 403
    error_code = ErrorCode.FORBIDDEN

    def __init__(self, message: str = "Access denied.", **kw: Any) -> None:
        super().__init__(message, **kw)


class UnauthorizedError(VertexOpsError):
    status_code = 401
    error_code = ErrorCode.UNAUTHORIZED

    def __init__(self, message: str = "Authentication required.", **kw: Any) -> None:
        super().__init__(message, **kw)


class ConflictError(VertexOpsError):
    status_code = 409
    error_code = ErrorCode.CONFLICT

    def __init__(self, message: str = "Resource conflict.", **kw: Any) -> None:
        super().__init__(message, **kw)


class DomainValidationError(VertexOpsError):
    """Raised by service-layer validation (distinct from request-body validation)."""

    status_code = 422
    error_code = ErrorCode.VALIDATION_ERROR

    def __init__(self, message: str = "Validation failed.", **kw: Any) -> None:
        super().__init__(message, **kw)


class RateLimitError(VertexOpsError):
    status_code = 429
    error_code = ErrorCode.RATE_LIMIT_EXCEEDED

    def __init__(self, message: str = "Rate limit exceeded.", **kw: Any) -> None:
        super().__init__(message, **kw)


class InternalError(VertexOpsError):
    status_code = 500
    error_code = ErrorCode.INTERNAL_ERROR

    def __init__(self, message: str = "An internal error occurred.", **kw: Any) -> None:
        super().__init__(message, **kw)
