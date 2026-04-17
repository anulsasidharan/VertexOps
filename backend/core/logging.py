"""Structured JSON logging for API and workers.

Usage
-----
Call ``configure_logging()`` once at application startup (lifespan or worker
boot).  Afterwards, standard ``logging.getLogger(__name__)`` calls emit
JSON-formatted records that carry the current request ID and auth subject
automatically via context variables.
"""

import json
import logging
import sys
import traceback
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Context variables — set by RequestContextMiddleware; read by the formatter
# ---------------------------------------------------------------------------

request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
auth_subject_var: ContextVar[Optional[str]] = ContextVar("auth_subject", default=None)


# ---------------------------------------------------------------------------
# JSON log formatter
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object."""

    # Fields whose values we always include (in this order)
    _BASE_FIELDS = ("timestamp", "level", "logger", "message")

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Request context — only added when set (API path; absent for workers)
        req_id = request_id_var.get()
        if req_id:
            payload["request_id"] = req_id

        auth_sub = auth_subject_var.get()
        if auth_sub:
            payload["auth_subject"] = auth_sub

        # Exception info
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.exc_text:
            payload["exception_text"] = record.exc_text

        # Stack info
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        # Any extra fields attached via ``logger.info("msg", extra={"foo": "bar"})``
        _standard_attrs = logging.LogRecord.__dict__.keys() | {
            "message", "asctime", "msg", "args", "exc_info", "exc_text",
            "stack_info", "created", "msecs", "relativeCreated", "thread",
            "threadName", "process", "processName", "pathname", "filename",
            "module", "funcName", "lineno", "levelno", "levelname", "name",
        }
        for key, value in record.__dict__.items():
            if key not in _standard_attrs:
                payload[key] = value

        return json.dumps(payload, default=str)


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def configure_logging(log_level: str = "INFO") -> None:
    """Configure root logger with JSON output to stdout.

    Call once at startup.  Safe to call multiple times (idempotent via the
    handler guard).
    """
    root = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root.setLevel(numeric_level)

    # Avoid duplicate handlers if called more than once
    if any(isinstance(h, logging.StreamHandler) and h.stream is sys.stdout
           for h in root.handlers):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)

    # Quieten noisy third-party loggers in production
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").propagate = True
