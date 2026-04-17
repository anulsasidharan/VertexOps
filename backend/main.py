"""VertexOps — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1 import router as v1_router
from backend.core.config import get_settings
from backend.core.exceptions import VertexOpsError
from backend.core.logging import configure_logging
from backend.core.middleware import (
    RequestContextMiddleware,
    domain_exception_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    settings = get_settings()
    configure_logging(settings.log_level)
    # Future: initialise DB pool, Redis, telemetry
    yield
    # Future: close DB pool, Redis connections


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="VertexOps",
        description="LLMOps platform for deploying, monitoring, and fine-tuning GenAI applications.",
        version="0.1.0",
        lifespan=lifespan,
        # Disable default 422 HTML handler so our envelope handler takes over
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    # ------------------------------------------------------------------
    # Middleware — outermost to innermost per LDL.md §2
    # 1. CORS
    # 2. Rate limiting (Task #10)
    # 3. Request context (request ID, auth subject placeholder)
    # ------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    # ------------------------------------------------------------------
    # Exception handlers
    # ------------------------------------------------------------------
    app.add_exception_handler(VertexOpsError, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ------------------------------------------------------------------
    # Routers
    # ------------------------------------------------------------------
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
