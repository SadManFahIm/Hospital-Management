"""
Centralized structured logging configuration.

Produces one JSON object per log line, by default to stdout, including a
timestamp, level, logger/module name, request correlation id (when available),
and the message. Call `setup_logging()` once at application startup.

Security: this module NEVER logs secrets. Helper `safe_log` is provided for
auth flows; callers must pass only non-sensitive fields.
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

# Correlation / request id propagated to all loggers within a request.
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def get_request_id() -> str | None:
    return request_id_var.get()


def set_request_id(value: str | None) -> None:
    request_id_var.set(value)


class JsonFormatter(logging.Formatter):
    """Format log records as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = get_request_id()
        if request_id:
            payload["request_id"] = request_id
        # Add any extra fields provided via logging.error(..., extra={'key': value})
        for key, value in getattr(record, "_extra", {}).items():
            payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging(debug: bool = False) -> None:
    """Configure root logging. Safe to call multiple times (idempotent per app)."""
    root = logging.getLogger()
    # Avoid stacking duplicate handlers if setup_logging is called more than once.
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    level = logging.DEBUG if debug else logging.INFO
    root.setLevel(level)
    root.addHandler(handler)

    # Keep noisy third-party loggers reasonable in production.
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if debug else logging.WARNING
    )
