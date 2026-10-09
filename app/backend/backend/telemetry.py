from __future__ import annotations

import json
import logging
from contextlib import AbstractContextManager
from datetime import UTC, datetime
from typing import Any

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import Span
from quart import Quart

from .config import Settings

_azure_monitor_configured = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in (
            "request_id",
            "request_method",
            "request_path",
            "response_status",
            "duration_ms",
            "work_item_id",
            "work_item_status",
            "cleanup_failure_count",
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = str(value)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def configure_telemetry(app: Quart, settings: Settings) -> None:
    global _azure_monitor_configured
    connection_string = settings.application_insights_connection_string
    if connection_string and not _azure_monitor_configured:
        configure_azure_monitor(connection_string=connection_string)
        _azure_monitor_configured = True


def start_request_span(
    method: str,
    path: str,
) -> AbstractContextManager[Span]:
    tracer = trace.get_tracer("ai-solution-starter.backend")
    scope = tracer.start_as_current_span(f"{method} {path}")
    span = scope.__enter__()
    span.set_attribute("http.request.method", method)
    span.set_attribute("url.path", path)
    return scope


def finish_request_span(
    scope: AbstractContextManager[Span] | None,
    status_code: int,
) -> None:
    if scope is None:
        return
    span = trace.get_current_span()
    span.set_attribute("http.response.status_code", status_code)
    scope.__exit__(None, None, None)
