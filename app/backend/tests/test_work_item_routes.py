from dataclasses import replace
from io import BytesIO

import pytest
from backend.app import create_app
from backend.repositories import RepositoryUnavailableError
from werkzeug.datastructures import FileStorage

from tests.conftest import FakeWorkItemRepository
from tests.helpers import pdf_bytes, work_item


@pytest.mark.asyncio
async def test_create_and_replay_work_item(client) -> None:
    headers = {"Idempotency-Key": "request-key-123"}
    first = await client.post(
        "/api/v1/work-items",
        headers=headers,
        files={
            "file": FileStorage(
                stream=BytesIO(pdf_bytes()),
                filename="example.pdf",
                content_type="application/pdf",
            )
        },
    )
    assert first.status_code == 201

    replay = await client.post(
        "/api/v1/work-items",
        headers=headers,
        files={
            "file": FileStorage(
                stream=BytesIO(pdf_bytes()),
                filename="example.pdf",
                content_type="application/pdf",
            )
        },
    )
    assert replay.status_code == 200
    assert replay.headers["Idempotent-Replayed"] == "true"


@pytest.mark.asyncio
async def test_missing_idempotency_key_returns_json_error(client) -> None:
    response = await client.post("/api/v1/work-items")
    payload = await response.get_json()
    assert response.status_code == 400
    assert payload["error"]["code"] == "missing_idempotency_key"
    assert response.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_missing_easy_auth_header_returns_json_error(settings, dependencies) -> None:
    app = create_app(
        replace(settings, local_auth_subject=None),
        dependencies,
    )
    async with app.test_app():
        response = await app.test_client().get("/api/v1/work-items")
    payload = await response.get_json()
    assert response.status_code == 401
    assert payload["error"]["code"] == "authentication_required"


@pytest.mark.asyncio
async def test_invalid_pdf_returns_json_error(client) -> None:
    response = await client.post(
        "/api/v1/work-items",
        headers={"Idempotency-Key": "request-key-123"},
        files={
            "file": FileStorage(
                stream=BytesIO(b"not a pdf"),
                filename="example.pdf",
                content_type="application/pdf",
            )
        },
    )
    payload = await response.get_json()
    assert response.status_code == 400
    assert payload["error"]["code"] == "invalid_pdf_signature"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("query", "code"),
    [
        ("status=unknown", "invalid_status"),
        ("page_size=0", "invalid_page_size"),
        ("page_size=not-a-number", "invalid_page_size"),
        (f"continuation_token={'x' * 4097}", "invalid_continuation_token"),
    ],
)
async def test_invalid_list_query_returns_json_error(client, query: str, code: str) -> None:
    response = await client.get(f"/api/v1/work-items?{query}")
    payload = await response.get_json()
    assert response.status_code == 400
    assert payload["error"]["code"] == code


@pytest.mark.asyncio
async def test_list_is_owner_scoped_and_filters_status(
    client,
    work_item_repository: FakeWorkItemRepository,
) -> None:
    own = work_item()
    other = work_item(
        item_id="7d57a43d-15b4-428e-88d4-16a1853eb2bb",
        owner_id="owner-2",
    )
    work_item_repository.records = {own.id: own, other.id: other}
    response = await client.get("/api/v1/work-items?status=queued")
    payload = await response.get_json()
    assert response.status_code == 200
    assert [item["id"] for item in payload["items"]] == [own.id]


@pytest.mark.asyncio
async def test_other_owner_receives_not_found(
    client,
    work_item_repository: FakeWorkItemRepository,
) -> None:
    other = work_item(owner_id="owner-2")
    work_item_repository.records[other.id] = other
    response = await client.get(f"/api/v1/work-items/{other.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_status_response_excludes_internal_fields(
    client,
    work_item_repository: FakeWorkItemRepository,
) -> None:
    record = work_item()
    work_item_repository.records[record.id] = record
    response = await client.get(f"/api/v1/work-items/{record.id}/status")
    payload = await response.get_json()
    assert response.status_code == 200
    assert set(payload) == {"id", "status", "updated_at", "error"}


@pytest.mark.asyncio
async def test_dependency_error_is_mapped_to_json(
    client,
    work_item_repository: FakeWorkItemRepository,
) -> None:
    work_item_repository.create_error = RepositoryUnavailableError("unavailable")
    response = await client.post(
        "/api/v1/work-items",
        headers={"Idempotency-Key": "request-key-123"},
        files={
            "file": FileStorage(
                stream=BytesIO(pdf_bytes()),
                filename="example.pdf",
                content_type="application/pdf",
            )
        },
    )
    payload = await response.get_json()
    assert response.status_code == 503
    assert payload["error"]["code"] == "work_item_create_failed"


@pytest.mark.asyncio
async def test_request_id_is_propagated(client) -> None:
    response = await client.get(
        "/api/v1/work-items",
        headers={"X-Request-ID": "caller-request-123"},
    )
    assert response.headers["X-Request-ID"] == "caller-request-123"


@pytest.mark.asyncio
async def test_unsupported_method_returns_json_error(client) -> None:
    response = await client.put("/api/v1/work-items")
    payload = await response.get_json()
    assert response.status_code == 405
    assert payload["error"]["code"] == "http_error"
