"""Celery queue names — single source of truth for routing."""

from kombu import Queue

QUEUE_INGEST = "ingest"
QUEUE_EMBED = "embed"
QUEUE_INDEX = "index"
QUEUE_EVAL = "eval"

QUEUES = [
    Queue(QUEUE_INGEST),
    Queue(QUEUE_EMBED),
    Queue(QUEUE_INDEX),
    Queue(QUEUE_EVAL),
]

TASK_ROUTES = {
    "backend.workers.tasks.ingest.*": {"queue": QUEUE_INGEST},
    "backend.workers.tasks.embed.*": {"queue": QUEUE_EMBED},
    "backend.workers.tasks.index_tasks.*": {"queue": QUEUE_INDEX},
    "backend.workers.tasks.eval.*": {"queue": QUEUE_EVAL},
    "backend.workers.tasks.pipeline.*": {"queue": QUEUE_INGEST},
}
