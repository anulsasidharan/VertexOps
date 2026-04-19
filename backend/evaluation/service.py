"""Evaluation service — case ingestion, metric computation, and snapshot persistence."""

import logging
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.evaluation.metrics import (
    CaseMetrics,
    aggregate_case_metrics,
    compute_case_metrics,
)
from backend.models.eval_case import EvalCase
from backend.models.metric_snapshot import MetricSnapshot
from backend.repositories.eval_case_repository import EvalCaseRepository
from backend.repositories.metric_snapshot_repository import MetricSnapshotRepository
from backend.repositories.run_repository import RunRepository

logger = logging.getLogger(__name__)


class EvaluationService:
    """Manages evaluation cases and metric aggregation for a run."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._run_repo = RunRepository(session)
        self._case_repo = EvalCaseRepository(session)
        self._snap_repo = MetricSnapshotRepository(session)

    async def add_case(
        self,
        run_id: uuid.UUID,
        question: str,
        predicted: str,
        ground_truth: Optional[str] = None,
        context: Optional[str] = None,
        latency_ms: float = 0.0,
        token_count: int = 0,
    ) -> EvalCase:
        """Compute metrics for a single case and persist it."""
        metrics = compute_case_metrics(
            question=question,
            predicted=predicted,
            ground_truth=ground_truth,
            context=context,
            latency_ms=latency_ms,
            token_count=token_count,
        )
        case = EvalCase(
            run_id=run_id,
            question=question,
            ground_truth=ground_truth,
            predicted=predicted,
            case_metrics=metrics.to_dict(),
            failure_type=metrics.failure_type,
        )
        await self._case_repo.add(case)
        return case

    async def ingest_cases(
        self,
        run_id: uuid.UUID,
        cases: list[dict[str, Any]],
    ) -> list[EvalCase]:
        """Validate and persist evaluation cases for a run (bulk ingest)."""
        if not cases:
            return []
        return await self.add_cases_bulk(run_id, cases)

    async def add_cases_bulk(
        self,
        run_id: uuid.UUID,
        cases: list[dict[str, Any]],
    ) -> list[EvalCase]:
        """Ingest multiple evaluation cases in one call."""
        results: list[EvalCase] = []
        for c in cases:
            ev_case = await self.add_case(
                run_id=run_id,
                question=c["question"],
                predicted=c.get("predicted", ""),
                ground_truth=c.get("ground_truth"),
                context=c.get("context"),
                latency_ms=c.get("latency_ms", 0.0),
                token_count=c.get("token_count", 0),
            )
            results.append(ev_case)
        return results

    async def compute_and_save_aggregate(self, run_id: uuid.UUID) -> MetricSnapshot:
        """Aggregate all case metrics for a run and persist a MetricSnapshot."""
        raw_cases = await self._case_repo.list_by_run(run_id)
        case_metrics: list[CaseMetrics] = []
        for c in raw_cases:
            m = c.case_metrics or {}
            case_metrics.append(
                CaseMetrics(
                    relevance=m.get("relevance", 0.0),
                    faithfulness=m.get("faithfulness", 0.0),
                    latency_ms=m.get("latency_ms", 0.0),
                    token_count=m.get("token_count", 0),
                    cost_usd=m.get("cost_usd", 0.0),
                    failure_type=m.get("failure_type"),
                )
            )

        agg = aggregate_case_metrics(case_metrics)
        snap = MetricSnapshot(run_id=run_id, snapshot_metrics=agg.to_dict())
        await self._snap_repo.add(snap)
        logger.info(
            "Saved metric snapshot run=%s cases=%d failures=%d",
            run_id,
            agg.case_count,
            agg.failure_count,
        )
        return snap

    async def get_latest_snapshot(self, run_id: uuid.UUID) -> Optional[MetricSnapshot]:
        snaps = await self._snap_repo.list_by_run(run_id)
        return snaps[-1] if snaps else None
