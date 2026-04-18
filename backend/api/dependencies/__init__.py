"""FastAPI shared dependencies."""

from backend.api.dependencies.auth import AuthContext, get_current_user, require_role

__all__ = ["AuthContext", "get_current_user", "require_role"]
