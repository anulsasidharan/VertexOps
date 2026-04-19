"""Unit tests for Celery app configuration, queues, and task dispatch."""


# ---------------------------------------------------------------------------
# Queue topology
# ---------------------------------------------------------------------------


def test_queue_names_defined():
    from backend.workers.queues import (
        QUEUE_EMBED,
        QUEUE_EVAL,
        QUEUE_INDEX,
        QUEUE_INGEST,
    )

    assert QUEUE_INGEST == "ingest"
    assert QUEUE_EMBED == "embed"
    assert QUEUE_INDEX == "index"
    assert QUEUE_EVAL == "eval"


def test_queues_list_has_four_entries():
    from backend.workers.queues import QUEUES

    assert len(QUEUES) == 4


def test_task_routes_cover_all_modules():
    from backend.workers.queues import TASK_ROUTES

    route_keys = " ".join(TASK_ROUTES.keys())
    assert "ingest" in route_keys
    assert "embed" in route_keys
    assert "index_tasks" in route_keys
    assert "eval" in route_keys


# ---------------------------------------------------------------------------
# Celery app config
# ---------------------------------------------------------------------------


def test_celery_app_is_celery_instance():
    from celery import Celery

    from backend.workers.celery_app import celery_app

    assert isinstance(celery_app, Celery)


def test_celery_app_name():
    from backend.workers.celery_app import celery_app

    assert celery_app.main == "vertexops"


def test_celery_app_uses_json_serializer():
    from backend.workers.celery_app import celery_app

    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"


def test_celery_app_acks_late():
    from backend.workers.celery_app import celery_app

    assert celery_app.conf.task_acks_late is True


def test_celery_app_prefetch_one():
    from backend.workers.celery_app import celery_app

    assert celery_app.conf.worker_prefetch_multiplier == 1


def test_celery_app_includes_all_task_modules():
    from backend.workers.celery_app import celery_app

    includes = celery_app.conf.include
    assert "backend.workers.tasks.ingest" in includes
    assert "backend.workers.tasks.embed" in includes
    assert "backend.workers.tasks.index_tasks" in includes
    assert "backend.workers.tasks.eval" in includes
    assert "backend.workers.tasks.pipeline" in includes


# ---------------------------------------------------------------------------
# Task registration
# ---------------------------------------------------------------------------


def test_parse_document_task_registered():
    from backend.workers.celery_app import celery_app
    from backend.workers.tasks import ingest  # noqa: F401

    assert "backend.workers.tasks.ingest.parse_document" in celery_app.tasks


def test_embed_chunks_task_registered():
    from backend.workers.celery_app import celery_app
    from backend.workers.tasks import embed  # noqa: F401

    assert "backend.workers.tasks.embed.embed_document_chunks" in celery_app.tasks


def test_build_index_task_registered():
    from backend.workers.celery_app import celery_app
    from backend.workers.tasks import index_tasks  # noqa: F401

    assert "backend.workers.tasks.index_tasks.build_index" in celery_app.tasks


def test_run_evaluation_task_registered():
    from backend.workers.celery_app import celery_app
    from backend.workers.tasks import eval as eval_module  # noqa: F401

    assert "backend.workers.tasks.eval.run_evaluation" in celery_app.tasks


# ---------------------------------------------------------------------------
# Task dispatch — queue routing verified via task metadata
# ---------------------------------------------------------------------------


def test_parse_document_task_queue():
    from backend.workers.tasks.ingest import parse_document

    assert parse_document.queue == "ingest"


def test_embed_chunks_task_queue():
    from backend.workers.tasks.embed import embed_document_chunks

    assert embed_document_chunks.queue == "embed"


def test_build_index_task_queue():
    from backend.workers.tasks.index_tasks import build_index

    assert build_index.queue == "index"


def test_run_evaluation_task_queue():
    from backend.workers.tasks.eval import run_evaluation

    assert run_evaluation.queue == "eval"


def test_parse_document_max_retries():
    from backend.workers.tasks.ingest import parse_document

    assert parse_document.max_retries == 3


def test_embed_chunks_max_retries():
    from backend.workers.tasks.embed import embed_document_chunks

    assert embed_document_chunks.max_retries == 3
