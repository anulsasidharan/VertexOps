"""Experiments API — CRUD and run-kickoff endpoints."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.core.db import get_db
from backend.core.exceptions import ForbiddenError
from backend.experiments.service import ExperimentService

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ExperimentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    index_id: Optional[uuid.UUID] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    id: uuid.UUID
    experiment_id: uuid.UUID
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExperimentResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: Optional[str] = None
    index_id: Optional[uuid.UUID] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, exp) -> "ExperimentResponse":
        return cls(
            id=exp.id,
            workspace_id=exp.workspace_id,
            name=exp.name,
            description=exp.description,
            index_id=exp.index_id,
            config=exp.experiment_config or {},
            created_at=exp.created_at,
            updated_at=exp.updated_at,
        )


class ExperimentListResponse(BaseModel):
    items: List[ExperimentResponse]
    total: int


class RunKickoffRequest(BaseModel):
    run_config: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

def get_experiment_service(db=Depends(get_db)) -> ExperimentService:
    return ExperimentService(db)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    body: ExperimentCreateRequest,
    auth: AuthContext = Depends(get_current_user),
    svc: ExperimentService = Depends(get_experiment_service),
) -> ExperimentResponse:
    if auth.workspace_id is None:
        raise ForbiddenError("No workspace associated with this account.")
    exp = await svc.create(
        workspace_id=auth.workspace_id,
        name=body.name,
        config=body.config,
        description=body.description,
        index_id=body.index_id,
    )
    return ExperimentResponse.from_orm(exp)


@router.get("", response_model=ExperimentListResponse)
async def list_experiments(
    auth: AuthContext = Depends(get_current_user),
    svc: ExperimentService = Depends(get_experiment_service),
) -> ExperimentListResponse:
    if auth.workspace_id is None:
        return ExperimentListResponse(items=[], total=0)
    experiments = await svc.list(auth.workspace_id)
    items = [ExperimentResponse.from_orm(e) for e in experiments]
    return ExperimentListResponse(items=items, total=len(items))


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: uuid.UUID,
    auth: AuthContext = Depends(get_current_user),
    svc: ExperimentService = Depends(get_experiment_service),
) -> ExperimentResponse:
    if auth.workspace_id is None:
        raise ForbiddenError("No workspace associated with this account.")
    exp = await svc.get(experiment_id, auth.workspace_id)
    return ExperimentResponse.from_orm(exp)


@router.post("/{experiment_id}/run", response_model=RunResponse, status_code=201)
async def kickoff_run(
    experiment_id: uuid.UUID,
    body: RunKickoffRequest,
    auth: AuthContext = Depends(get_current_user),
    svc: ExperimentService = Depends(get_experiment_service),
) -> RunResponse:
    if auth.workspace_id is None:
        raise ForbiddenError("No workspace associated with this account.")
    run = await svc.kickoff_run(
        experiment_id=experiment_id,
        workspace_id=auth.workspace_id,
        run_config=body.run_config,
    )
    return RunResponse.model_validate(run)
