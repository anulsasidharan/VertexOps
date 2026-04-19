"""Prometheus metrics registry and optional OpenTelemetry trace initialisation."""

from __future__ import annotations

import logging

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Histogram,
    Info,
    generate_latest,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prometheus metrics — module-level singletons (safe for multi-process via
# PROMETHEUS_MULTIPROC_DIR when configured).
# ---------------------------------------------------------------------------

APP_INFO = Info("vertexops_app", "Application metadata")

HTTP_REQUESTS_TOTAL = Counter(
    "vertexops_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "vertexops_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

CELERY_TASKS_TOTAL = Counter(
    "vertexops_celery_tasks_total",
    "Total Celery task executions",
    ["task_name", "state"],
)

CELERY_TASK_DURATION_SECONDS = Histogram(
    "vertexops_celery_task_duration_seconds",
    "Celery task duration in seconds",
    ["task_name"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0),
)

RAG_QUERY_LATENCY_SECONDS = Histogram(
    "vertexops_rag_query_latency_seconds",
    "End-to-end RAG query latency in seconds",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
)

EVAL_RUNS_TOTAL = Counter(
    "vertexops_eval_runs_total",
    "Total evaluation runs",
    ["status"],
)

INGEST_DOCUMENTS_TOTAL = Counter(
    "vertexops_ingest_documents_total",
    "Total documents ingested",
    ["status"],
)


def initialise_app_info(version: str, env: str) -> None:
    APP_INFO.info({"version": version, "env": env})


# ---------------------------------------------------------------------------
# Prometheus scrape helpers
# ---------------------------------------------------------------------------


def get_metrics_output() -> tuple[bytes, str]:
    """Return (body, content_type) for the /metrics scrape endpoint."""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST


# ---------------------------------------------------------------------------
# OpenTelemetry — optional; initialised only when endpoint is configured
# ---------------------------------------------------------------------------


def setup_otel(service_name: str, endpoint: str | None) -> None:
    """Configure OTLP trace exporter when endpoint is provided."""
    if not endpoint:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry tracing initialised → %s", endpoint)
    except ImportError:
        logger.warning(
            "opentelemetry-sdk or opentelemetry-exporter-otlp-proto-grpc not installed; "
            "OTel tracing disabled."
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("OTel initialisation failed: %s", exc)
