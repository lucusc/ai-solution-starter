from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from quart import Blueprint, current_app, g, jsonify, request

from ..auth import AuthenticatedUser
from ..config import Settings
from ..dependencies import AppDependencies
from ..errors import RequestValidationError
from ..models import (
    WorkItemListResponse,
    WorkItemResponse,
    WorkItemStatus,
    WorkItemStatusResponse,
)
from ..pdf import validate_pdf_upload

work_items_blueprint = Blueprint("work_items", __name__, url_prefix="/api/v1")


def _dependencies() -> AppDependencies:
    return cast(AppDependencies, current_app.extensions["dependencies"])


def _settings() -> Settings:
    return cast(Settings, current_app.extensions["settings"])


def _user() -> AuthenticatedUser:
    return cast(AuthenticatedUser, g.authenticated_user)


def _work_item_id(value: str) -> str:
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise RequestValidationError(
            "invalid_work_item_id", "The work-item ID is invalid."
        ) from exc
    if str(parsed) != value.lower():
        raise RequestValidationError("invalid_work_item_id", "The work-item ID is invalid.")
    return str(parsed)


@work_items_blueprint.post("/work-items")
async def create_work_item() -> tuple[Any, int, dict[str, str]]:
    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key is None:
        raise RequestValidationError(
            "missing_idempotency_key", "The Idempotency-Key header is required."
        )
    files = await request.files
    pdf = await validate_pdf_upload(
        files.get("file"),
        max_size_bytes=_settings().max_pdf_size_bytes,
    )
    try:
        result = await _dependencies().work_item_service.create(
            _user().subject,
            idempotency_key,
            pdf,
        )
    except ValueError as exc:
        raise RequestValidationError("invalid_idempotency_key", str(exc)) from exc
    finally:
        pdf.close()

    response = jsonify(WorkItemResponse.from_record(result.record).model_dump(mode="json"))
    headers = {"Idempotent-Replayed": "true"} if result.replayed else {}
    return response, 200 if result.replayed else 201, headers


@work_items_blueprint.get("/work-items")
async def list_work_items() -> Any:
    settings = _settings()
    status_value = request.args.get("status")
    status: WorkItemStatus | None = None
    if status_value:
        try:
            status = WorkItemStatus(status_value)
        except ValueError as exc:
            raise RequestValidationError("invalid_status", "The status filter is invalid.") from exc
    page_size_value = request.args.get("page_size")
    page_size = settings.default_page_size
    if page_size_value is not None:
        try:
            page_size = int(page_size_value)
        except ValueError as exc:
            raise RequestValidationError(
                "invalid_page_size", "The page size must be an integer."
            ) from exc
    if not 1 <= page_size <= settings.max_page_size:
        raise RequestValidationError(
            "invalid_page_size",
            f"The page size must be between 1 and {settings.max_page_size}.",
        )
    continuation_token = request.args.get("continuation_token")
    if continuation_token and len(continuation_token) > 4096:
        raise RequestValidationError(
            "invalid_continuation_token", "The continuation token is invalid."
        )
    page = await _dependencies().work_item_service.list(
        _user().subject,
        status=status,
        page_size=page_size,
        continuation_token=continuation_token,
    )
    response = WorkItemListResponse(
        items=[WorkItemResponse.from_record(item) for item in page.items],
        continuation_token=page.continuation_token,
    )
    return jsonify(response.model_dump(mode="json"))


@work_items_blueprint.get("/work-items/<work_item_id>")
async def get_work_item(work_item_id: str) -> Any:
    record = await _dependencies().work_item_service.get(
        _user().subject,
        _work_item_id(work_item_id),
    )
    return jsonify(WorkItemResponse.from_record(record).model_dump(mode="json"))


@work_items_blueprint.get("/work-items/<work_item_id>/status")
async def get_work_item_status(work_item_id: str) -> Any:
    record = await _dependencies().work_item_service.get(
        _user().subject,
        _work_item_id(work_item_id),
    )
    return jsonify(WorkItemStatusResponse.from_record(record).model_dump(mode="json"))
