"""Eval queue tasks — run evaluation jobs and persist metric snapshots."""

import logging
from uuid import UUID

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="backend.workers.tasks.eval.run_evaluation",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    queue="eval",
)
def run_evaluation(self, run_id: str) -> dict:
    """Execute an evaluation run and persist metric snapshots."""
    logger.info("run_evaluation: run=%s", run_id)
    try:
        import asyncio

        from backend.workers._runner import run_eval

        result = asyncio.run(run_eval(UUID(run_id)))
        return result
    except Exception as exc:
        logger.exception("run_evaluation failed: %s", exc)
        raise self.retry(exc=exc)
