"""Experiment registry service — CRUD, config hashing, and run kickoff."""

import hashlib
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import ForbiddenError, NotFoundError
from backend.models.experiment import Experiment
from backend.models.run import Run
from backend.repositories.experiment_repository import ExperimentRepository
from backend.repositories.run_repository import RunRepository

logger = logging.getLogger(__name__)


def _compute_config_hash(config: Dict[str, Any]) -> str:
    """SHA-256 of canonically-sorted JSON for reproducible config identity."""
    serialised = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialised.encode()).hexdigest()


class ExperimentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._exp_repo = ExperimentRepository(session)
        self._run_repo = RunRepository(session)

    async def create(
        self,
        workspace_id: uuid.UUID,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        index_id: Optional[uuid.UUID] = None,
    ) -> Experiment:
        exp = Experiment(
            workspace_id=workspace_id,
            name=name,
            description=description,
            index_id=index_id,
            experiment_config=config or {},
        )
        await self._exp_repo.add(exp)
        logger.info("Created experiment id=%s name=%r", exp.id, name)
        return exp

    async def get(
        self, experiment_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Experiment:
        exp = await self._exp_repo.get(experiment_id)
        if exp is None:
            raise NotFoundError(f"Experiment {experiment_id} not found.")
        if exp.workspace_id != workspace_id:
            raise ForbiddenError("Experiment does not belong to this workspace.")
        return exp

    async def list(self, workspace_id: uuid.UUID) -> List[Experiment]:
        return await self._exp_repo.list_by_workspace(workspace_id)

    async def delete(
        self, experiment_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> None:
        exp = await self.get(experiment_id, workspace_id)
        await self._exp_repo.delete(exp)

    async def kickoff_run(
        self,
        experiment_id: uuid.UUID,
        workspace_id: uuid.UUID,
        run_config: Optional[Dict[str, Any]] = None,
    ) -> Run:
        """Create a queued Run for the experiment and return it."""
        exp = await self.get(experiment_id, workspace_id)
        merged_config = {**(exp.experiment_config or {}), **(run_config or {})}
        run = Run(
            experiment_id=exp.id,
            status="queued",
            run_logs={"config_hash": _compute_config_hash(merged_config)},
        )
        await self._run_repo.add(run)
        logger.info("Kicked off run id=%s for experiment=%s", run.id, experiment_id)
        return run
