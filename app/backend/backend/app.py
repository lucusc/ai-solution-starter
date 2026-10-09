from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any

from quart import Quart, Response, g, jsonify, request
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from .auth import authenticate_request
from .config import Settings
from .dependencies import AppDependencies, build_dependencies
from .errors import AppError
from .routes import health_blueprint, work_items_blueprint
from .telemetry import (
    configure_logging,
    configure_telemetry,
    finish_request_span,
    start_request_span,
)

logger = logging.getLogger(__name__)
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _request_id() -> str:
    candidate = request.headers.get("X-Request-ID", "")
    if REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid.uuid4())


def _error_payload(error: AppError) -> dict[str, Any]:
    return {
        "error": {
            "code": error.code,
            "message": error.message,
            "request_id": getattr(g, "request_id", str(uuid.uuid4())),
            "details": error.details,
        }
    }


def create_app(
    settings: Settings | None = None,
    dependencies: AppDependencies | None = None,
) -> Quart:
    resolved_settings = settings or Settings.from_environment()
    resolved_dependencies = dependencies or build_dependencies(resolved_settings)

    configure_logging(resolved_settings.log_level)
    app = Quart(__name__)
    app.config["MAX_CONTENT_LENGTH"] = resolved_settings.max_pdf_size_bytes + (1024 * 1024)
    app.extensions["settings"] = resolved_settings
    app.extensions["dependencies"] = resolved_dependencies
    app.extensions["readiness_cache"] = {}

    @app.before_request
    async def prepare_request() -> None:
        g.request_id = _request_id()
        g.request_started = time.perf_counter()
        g.request_span_scope = start_request_span(request.method, request.path)
        if request.path.startswith("/api/v1/"):
            g.authenticated_user = authenticate_request(request, resolved_settings)

    @app.after_request
    async def complete_request(response: Response) -> Response:
        request_id = getattr(g, "request_id", str(uuid.uuid4()))
        response.headers["X-Request-ID"] = request_id
        started = getattr(g, "request_started", time.perf_counter())
        logger.info(
            "Request completed.",
            extra={
                "request_id": request_id,
                "request_method": request.method,
                "request_path": request.path,
                "response_status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        finish_request_span(
            getattr(g, "request_span_scope", None),
            response.status_code,
        )
        return response

    @app.errorhandler(AppError)
    async def handle_app_error(error: AppError) -> tuple[Any, int]:
        return jsonify(_error_payload(error)), error.status_code

    @app.errorhandler(RequestEntityTooLarge)
    async def handle_too_large(_: RequestEntityTooLarge) -> tuple[Any, int]:
        error = AppError(
            "pdf_too_large",
            "The uploaded PDF exceeds the maximum allowed size.",
            413,
        )
        return jsonify(_error_payload(error)), 413

    @app.errorhandler(HTTPException)
    async def handle_http_error(error: HTTPException) -> tuple[Any, int]:
        app_error = AppError(
            "http_error",
            error.description or "The request could not be completed.",
            error.code or 500,
        )
        return jsonify(_error_payload(app_error)), app_error.status_code

    @app.errorhandler(Exception)
    async def handle_unexpected_error(error: Exception) -> tuple[Any, int]:
        logger.exception(
            "Unhandled request error.",
            extra={"request_id": getattr(g, "request_id", None)},
        )
        app_error = AppError(
            "internal_error",
            "The request could not be completed.",
            500,
        )
        return jsonify(_error_payload(app_error)), 500

    @app.after_serving
    async def close_dependencies() -> None:
        await resolved_dependencies.close()

    app.register_blueprint(health_blueprint)
    app.register_blueprint(work_items_blueprint)
    configure_telemetry(app, resolved_settings)
    return app
