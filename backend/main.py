"""VertexOps — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1 import router as v1_router
from backend.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
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
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
