"""Subject/body builders for supported notification event types."""

from typing import Any, Dict, Tuple


def eval_completed_email(payload: Dict[str, Any]) -> Tuple[str, str]:
    run_id = payload.get("run_id", "?")
    subject = f"[VertexOps] Evaluation run {run_id} completed"
    body = (
        f"Evaluation run {run_id} finished with status {payload.get('status', 'unknown')}.\n"
        f"Experiment: {payload.get('experiment_id', 'n/a')}\n"
    )
    return subject, body


def eval_completed_sms(payload: Dict[str, Any]) -> str:
    run_id = payload.get("run_id", "?")
    status = payload.get("status", "?")
    return f"VertexOps eval {run_id} done: {status}"


def deployment_changed_email(payload: Dict[str, Any]) -> Tuple[str, str]:
    dep = payload.get("deployment_id", "?")
    subject = f"[VertexOps] Deployment {dep} updated"
    body = str(payload.get("summary", "Deployment metadata changed."))
    return subject, body


def critical_failure_email(payload: Dict[str, Any]) -> Tuple[str, str]:
    subject = "[VertexOps] Critical failure alert"
    body = str(payload.get("message", "See logs for details."))
    return subject, body
