"""Evaluations API — start runs, status, and report artifacts."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.core.db import get_db
from backend.core.exceptions import ForbiddenError, NotFoundError
from backend.evaluation.lifecycle import EvaluationLifecycleService
from backend.ingestion.storage.base import artifact_storage_key
from backend.ingestion.storage.service import get_storage_backend

router = APIRouter()


class EvaluationCaseIn(BaseModel):
    question: str = Field(..., min_length=1)
    predicted: str = ""
    ground_truth: Optional[str] = None
    context: Optional[str] = None
    latency_ms: float = 0.0
    token_count: int = 0


class EvaluationCreateRequest(BaseModel):
    experiment_id: uuid.UUID
    cases: list[EvaluationCaseIn] = Field(..., min_length=1)


class EvaluationCreateResponse(BaseModel):
    id: uuid.UUID
    status: str


class EvaluationDetailResponse(BaseModel):
    id: uuid.UUID
    experiment_id: uuid.UUID
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    artifact_uri: Optional[str] = None
    metrics: Optional[dict[str, Any]] = None


def get_evaluation_lifecycle_service(
    db=Depends(get_db),
) -> EvaluationLifecycleService:
    return EvaluationLifecycleService(db)


def _enqueue_evaluation_worker(run_id: uuid.UUID) -> None:
    from backend.workers.tasks.eval import run_evaluation

    run_evaluation.delay(str(run_id))


@router.post("", response_model=EvaluationCreateResponse, status_code=201)
async def create_evaluation(
    body: EvaluationCreateRequest,
    auth: AuthContext = Depends(get_current_user),
    session=Depends(get_db),
    lifecycle: EvaluationLifecycleService = Depends(get_evaluation_lifecycle_service),
) -> EvaluationCreateResponse:
    if auth.workspace_id is None:
        raise ForbiddenError("No workspace associated with this account.")
    cases_payload = [c.model_dump() for c in body.cases]
    run = await lifecycle.start_evaluation(
        workspace_id=auth.workspace_id,
        experiment_id=body.experiment_id,
        cases=cases_payload,
    )
    await session.commit()
    _enqueue_evaluation_worker(run.id)
    return EvaluationCreateResponse(id=run.id, status=run.status)


@router.get("/{evaluation_id}", response_model=EvaluationDetailResponse)
async def get_evaluation(
    evaluation_id: uuid.UUID,
    auth: AuthContext = Depends(get_current_user),
    lifecycle: EvaluationLifecycleService = Depends(get_evaluation_lifecycle_service),
) -> EvaluationDetailResponse:
    if auth.workspace_id is None:
        raise ForbiddenError("No workspace associated with this account.")
    detail = await lifecycle.get_detail(evaluation_id, auth.workspace_id)
    return EvaluationDetailResponse.model_validate(detail)


@router.get("/{evaluation_id}/report")
async def get_evaluation_report(
    evaluation_id: uuid.UUID,
    report_format: Literal["json", "html"] = Query("json", alias="format"),
    auth: AuthContext = Depends(get_current_user),
    lifecycle: EvaluationLifecycleService = Depends(get_evaluation_lifecycle_service),
) -> Response:
    if auth.workspace_id is None:
        raise ForbiddenError("No workspace associated with this account.")
    run = await lifecycle.get_run_for_workspace(evaluation_id, auth.workspace_id)
    logs = run.run_logs or {}
    if report_format == "html":
        key = logs.get("artifact_html_key") or artifact_storage_key(evaluation_id, "report.html")
        media_type = "text/html; charset=utf-8"
    else:
        key = logs.get("artifact_key") or artifact_storage_key(evaluation_id, "report.json")
        media_type = "application/json"
    storage = get_storage_backend()
    try:
        data = await storage.get(key)
    except NotFoundError as exc:
        raise NotFoundError("Report not found or not ready yet.") from exc
    return Response(content=data, media_type=media_type)
