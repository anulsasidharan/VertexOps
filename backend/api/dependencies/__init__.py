"""FastAPI shared dependencies."""

from backend.api.dependencies.auth import AuthContext, get_current_user, require_role
from backend.api.dependencies.rate_limit import rate_limit

__all__ = ["AuthContext", "get_current_user", "rate_limit", "require_role"]
