"""Persist orchestration decisions onto experiment runs."""

import logging
import uuid
from typing import Any, Callable, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.orchestration.optimization_graph import OptimizationState, build_optimization_graph
from backend.repositories.run_repository import RunRepository

logger = logging.getLogger(__name__)


class OrchestrationService:
    """Runs the optimization graph and merges outputs into ``Run.run_logs``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._run_repo = RunRepository(session)

    async def propose_and_record_iteration(
        self,
        run_id: uuid.UUID,
        *,
        failure_breakdown: Dict[str, int],
        trial_score: float,
        current_config: Dict[str, Any],
        best_score: float,
        best_config: Dict[str, Any],
        iteration: int,
        max_iterations: int,
        strategy_fn: Optional[Callable[[OptimizationState], str]] = None,
    ) -> Dict[str, Any]:
        graph = build_optimization_graph(strategy_fn=strategy_fn)
        state: OptimizationState = {
            "iteration": iteration,
            "max_iterations": max_iterations,
            "failure_breakdown": failure_breakdown,
            "trial_score": trial_score,
            "current_config": current_config,
            "best_score": best_score,
            "best_config": best_config,
        }
        result: Dict[str, Any] = dict(graph.invoke(state))

        run = await self._run_repo.get(run_id)
        if run is None:
            logger.warning("Orchestration: run %s not found; skipping persist", run_id)
            return result

        orch = (run.run_logs or {}).get("orchestration") or {}
        steps = list(orch.get("steps", []))
        steps.append(
            {
                "iteration": iteration,
                "last_strategy": result.get("last_strategy"),
                "rollback_reason": result.get("rollback_reason"),
                "failure_category": result.get("failure_category"),
                "config_after": result.get("current_config"),
            }
        )
        merged = {
            **(run.run_logs or {}),
            "orchestration": {
                **orch,
                "steps": steps,
                "latest": result,
            },
        }
        run.run_logs = merged
        await self._session.flush()
        logger.info(
            "Orchestration recorded run=%s iteration=%s strategy=%r rollback=%r",
            run_id,
            iteration,
            result.get("last_strategy"),
            result.get("rollback_reason"),
        )
        return result
