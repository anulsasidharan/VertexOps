"""Structured audit logging for sensitive platform operations."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any
from uuid import UUID

logger = logging.getLogger("vertexops.audit")


class AuditEvent(str, Enum):
    # Auth
    USER_LOGIN = "user.login"
    USER_LOGIN_FAILED = "user.login_failed"
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    # Documents
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_DELETED = "document.deleted"
    # Indexes
    INDEX_CREATED = "index.created"
    INDEX_REBUILT = "index.rebuilt"
    # Experiments & evaluation
    EXPERIMENT_CREATED = "experiment.created"
    EXPERIMENT_RUN_STARTED = "experiment.run_started"
    EVAL_STARTED = "eval.started"
    EVAL_COMPLETED = "eval.completed"
    # Config / deployment
    CONFIG_CHANGED = "config.changed"
    DEPLOYMENT_TRIGGERED = "deployment.triggered"


def emit(
    event: AuditEvent,
    actor_id: UUID | None = None,
    workspace_id: UUID | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    outcome: str = "success",
) -> None:
    """Emit a structured audit log entry.

    Records are JSON-serialisable so they can be shipped to GCP Cloud Logging,
    a SIEM, or any structured log pipeline without additional transformation.
    Never include raw secrets, PII beyond identifiers, or full request bodies.
    """
    record: dict[str, Any] = {
        "audit": True,
        "event": event.value,
        "outcome": outcome,
    }
    if actor_id is not None:
        record["actor_id"] = str(actor_id)
    if workspace_id is not None:
        record["workspace_id"] = str(workspace_id)
    if resource_id is not None:
        record["resource_id"] = resource_id
    if details:
        # Explicitly strip any key that smells like a secret
        safe = {
            k: v
            for k, v in details.items()
            if not any(tok in k.lower() for tok in ("secret", "password", "token", "key", "pepper"))
        }
        record["details"] = safe

    logger.info("AUDIT", extra={"json_fields": record})
