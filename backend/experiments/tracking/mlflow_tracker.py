"""Optional MLflow logging for evaluation runs — failures never propagate."""

import logging
from collections.abc import Mapping
from typing import Any

logger = logging.getLogger(__name__)


def try_log_evaluation_to_mlflow(
    *,
    run_id: str,
    experiment_id: str,
    metrics: Mapping[str, Any],
    params: Mapping[str, Any],
) -> None:
    """Emit evaluation params and numeric metrics to MLflow when enabled.

    Swallows all errors so core persistence and eval workflows are unaffected.
    """
    from backend.core.config import get_settings

    settings = get_settings()
    if not settings.mlflow_enabled or not settings.mlflow_tracking_uri:
        return

    try:
        import mlflow
    except ImportError:
        logger.info("mlflow package not installed; skipping tracking for run %s", run_id)
        return

    flat_params: dict[str, str] = {}
    for key, val in {**params, "vertexops_run_id": run_id, "experiment_id": experiment_id}.items():
        if val is None:
            continue
        flat_params[str(key)] = str(val)[:500]

    try:
        mlflow.set_tracking_uri(str(settings.mlflow_tracking_uri))
        mlflow.set_experiment(settings.mlflow_experiment_name)
        with mlflow.start_run(run_name=f"eval-{run_id[:8]}"):
            for k, v in flat_params.items():
                mlflow.log_param(k, v)
            for k, v in (metrics or {}).items():
                if isinstance(v, bool):
                    mlflow.log_metric(k, float(int(v)))
                elif isinstance(v, (int, float)):
                    mlflow.log_metric(str(k), float(v))
    except Exception as exc:
        logger.warning(
            "MLflow logging failed (non-fatal) run=%s: %s",
            run_id,
            exc,
            exc_info=logger.isEnabledFor(logging.DEBUG),
        )
