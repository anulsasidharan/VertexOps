"""Start and query evaluation runs (runs with eval cases) for the HTTP API."""

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundError
from backend.evaluation.service import EvaluationService
from backend.experiments.service import ExperimentService
from backend.models.metric_snapshot import MetricSnapshot
from backend.models.run import Run
from backend.repositories.run_repository import RunRepository

logger = logging.getLogger(__name__)


class EvaluationLifecycleService:
    """Creates evaluation runs under experiments and loads their status."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._exp_svc = ExperimentService(session)
        self._run_repo = RunRepository(session)
        self._eval_svc = EvaluationService(session)

    async def start_evaluation(
        self,
        *,
        workspace_id: uuid.UUID,
        experiment_id: uuid.UUID,
        cases: List[Dict[str, Any]],
    ) -> Run:
        await self._exp_svc.get(experiment_id, workspace_id)
        run = Run(
            experiment_id=experiment_id,
            status="queued",
            run_logs={"kind": "evaluation"},
        )
        await self._run_repo.add(run)
        await self._eval_svc.ingest_cases(run.id, cases)
        logger.info("Queued evaluation run id=%s experiment=%s", run.id, experiment_id)
        return run

    async def get_run_for_workspace(
        self, run_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Run:
        run = await self._run_repo.get(run_id)
        if run is None:
            raise NotFoundError(f"Evaluation run {run_id} not found.")
        await self._exp_svc.get(run.experiment_id, workspace_id)
        return run

    async def get_detail(
        self, run_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Dict[str, Any]:
        run = await self.get_run_for_workspace(run_id, workspace_id)
        snap: Optional[MetricSnapshot] = await self._eval_svc.get_latest_snapshot(
            run.id
        )
        return {
            "id": run.id,
            "experiment_id": run.experiment_id,
            "status": run.status,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "artifact_uri": run.artifact_uri,
            "metrics": snap.snapshot_metrics if snap else None,
        }
