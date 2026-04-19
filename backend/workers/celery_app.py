"""Celery application factory and singleton."""

from celery import Celery

from backend.workers.queues import QUEUES, TASK_ROUTES


def create_celery_app() -> Celery:
    """Build and configure the Celery app from application settings."""
    from backend.core.config import get_settings

    settings = get_settings()

    app = Celery("vertexops")

    app.conf.update(
        broker_url=settings.redis_broker_url,
        result_backend=settings.celery_result_backend,
        task_queues=QUEUES,
        task_routes=TASK_ROUTES,
        # Serialisation
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        # Reliability
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        # Retry defaults (override per task as needed)
        task_max_retries=3,
        task_default_retry_delay=30,  # seconds
        # Worker
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=500,
        # Timezone
        timezone="UTC",
        enable_utc=True,
        # Auto-discover tasks in backend.workers.tasks package
        include=[
            "backend.workers.tasks.ingest",
            "backend.workers.tasks.embed",
            "backend.workers.tasks.index_tasks",
            "backend.workers.tasks.eval",
            "backend.workers.tasks.pipeline",
        ],
    )

    return app


celery_app = create_celery_app()
