"""Indexes API — create, list, retrieve, and rebuild vector indexes."""

import hashlib
import json
from datetime import datetime
from typing import Annotated, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user
from backend.api.dependencies.auth import AuthContext
from backend.core.db import get_db
from backend.core.exceptions import ForbiddenError, NotFoundError
from backend.models.index import VectorIndex
from backend.repositories.index_repository import IndexRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class IndexCreateRequest(BaseModel):
    name: str
    vector_backend: str = "pinecone"
    namespace: Optional[str] = None
    index_config: Optional[dict[str, Any]] = None


class IndexResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    vector_backend: Optional[str]
    namespace: Optional[str]
    config_hash: Optional[str]
    index_config: Optional[dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IndexListResponse(BaseModel):
    items: list[IndexResponse]
    total: int


# ---------------------------------------------------------------------------
# Service helpers
# ---------------------------------------------------------------------------


def _compute_config_hash(config: Optional[dict[str, Any]]) -> Optional[str]:
    if not config:
        return None
    serialised = json.dumps(config, sort_keys=True)
    return hashlib.sha256(serialised.encode()).hexdigest()


def _require_workspace(auth: AuthContext) -> UUID:
    if auth.workspace_id is None:
        raise ForbiddenError("This endpoint requires a workspace-scoped token.")
    return auth.workspace_id


def get_index_service(db: AsyncSession = Depends(get_db)) -> IndexRepository:
    return IndexRepository(db)


async def _get_owned(repo: IndexRepository, workspace_id: UUID, index_id: UUID) -> VectorIndex:
    idx = await repo.get(index_id)
    if idx is None:
        raise NotFoundError(f"Index {index_id} not found.")
    if idx.workspace_id != workspace_id:
        raise ForbiddenError("Index does not belong to this workspace.")
    return idx


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("", response_model=IndexResponse, status_code=status.HTTP_201_CREATED)
async def create_index(
    req: IndexCreateRequest,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    repo: IndexRepository = Depends(get_index_service),
) -> IndexResponse:
    workspace_id = _require_workspace(auth)
    idx = VectorIndex(
        workspace_id=workspace_id,
        name=req.name,
        vector_backend=req.vector_backend,
        namespace=req.namespace,
        index_config=req.index_config,
        config_hash=_compute_config_hash(req.index_config),
        status="building",
    )
    idx = await repo.add(idx)
    return IndexResponse.model_validate(idx)


@router.get("", response_model=IndexListResponse)
async def list_indexes(
    auth: Annotated[AuthContext, Depends(get_current_user)],
    repo: IndexRepository = Depends(get_index_service),
) -> IndexListResponse:
    workspace_id = _require_workspace(auth)
    items = await repo.list_by_workspace(workspace_id)
    return IndexListResponse(
        items=[IndexResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get("/{index_id}", response_model=IndexResponse)
async def get_index(
    index_id: UUID,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    repo: IndexRepository = Depends(get_index_service),
) -> IndexResponse:
    workspace_id = _require_workspace(auth)
    idx = await _get_owned(repo, workspace_id, index_id)
    return IndexResponse.model_validate(idx)


@router.post("/{index_id}/rebuild", response_model=IndexResponse)
async def rebuild_index(
    index_id: UUID,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    repo: IndexRepository = Depends(get_index_service),
) -> IndexResponse:
    workspace_id = _require_workspace(auth)
    idx = await _get_owned(repo, workspace_id, index_id)
    idx.status = "building"
    await repo.session.flush()
    await repo.session.refresh(idx)
    return IndexResponse.model_validate(idx)
