"""Index queue tasks — build and update vector index status."""

import logging
from uuid import UUID

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="backend.workers.tasks.index_tasks.build_index",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    queue="index",
)
def build_index(self, index_id: str, workspace_id: str) -> dict:
    """Trigger an index build and update status to ready/failed on completion."""
    logger.info("build_index: index=%s ws=%s", index_id, workspace_id)
    try:
        import asyncio

        from backend.workers._runner import run_build_index

        result = asyncio.run(run_build_index(UUID(index_id), UUID(workspace_id)))
        return result
    except Exception as exc:
        logger.exception("build_index failed: %s", exc)
        raise self.retry(exc=exc)
