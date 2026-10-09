import pytest
from backend.errors import DependencyError, NotFoundError
from backend.models import WorkItemStatus
from backend.repositories import RepositoryError, RepositoryUnavailableError
from backend.services import WorkItemService
from backend.services.work_items import (
    deterministic_work_item_id,
    idempotency_key_hash,
)

from tests.conftest import FakeBlobRepository, FakeWorkItemRepository
from tests.helpers import validated_pdf, work_item


@pytest.mark.asyncio
async def test_create_queues_record_and_uploads_blob() -> None:
    records = FakeWorkItemRepository()
    blobs = FakeBlobRepository()
    service = WorkItemService(records, blobs)
    pdf = validated_pdf()
    try:
        result = await service.create("owner-1", "request-key-123", pdf)
    finally:
        pdf.close()
    assert result.record.status is WorkItemStatus.QUEUED
    assert result.record.source.blob_name in blobs.blobs


@pytest.mark.asyncio
async def test_repeated_key_replays_existing_record() -> None:
    records = FakeWorkItemRepository()
    blobs = FakeBlobRepository()
    service = WorkItemService(records, blobs)
    first_pdf = validated_pdf()
    second_pdf = validated_pdf("different.pdf")
    try:
        first = await service.create("owner-1", "request-key-123", first_pdf)
        second = await service.create("owner-1", "request-key-123", second_pdf)
    finally:
        first_pdf.close()
        second_pdf.close()
    assert second.replayed is True
    assert second.record.id == first.record.id
    assert len(blobs.blobs) == 1


@pytest.mark.asyncio
async def test_blob_failure_marks_record_failed() -> None:
    records = FakeWorkItemRepository()
    blobs = FakeBlobRepository(upload_error=RepositoryUnavailableError("unavailable"))
    service = WorkItemService(records, blobs)
    pdf = validated_pdf()
    with pytest.raises(DependencyError):
        try:
            await service.create("owner-1", "request-key-123", pdf)
        finally:
            pdf.close()
    record = next(iter(records.records.values()))
    assert record.status is WorkItemStatus.FAILED
    assert record.error is not None
    assert record.error.code == "blob_upload_failed"


@pytest.mark.asyncio
async def test_submitted_record_failure_does_not_upload_blob() -> None:
    records = FakeWorkItemRepository(create_error=RepositoryUnavailableError("unavailable"))
    blobs = FakeBlobRepository()
    service = WorkItemService(records, blobs)
    pdf = validated_pdf()
    with pytest.raises(DependencyError):
        try:
            await service.create("owner-1", "request-key-123", pdf)
        finally:
            pdf.close()
    assert blobs.blobs == {}


@pytest.mark.asyncio
async def test_failed_state_update_failure_is_logged(caplog) -> None:
    records = FakeWorkItemRepository(
        replace_error=RepositoryUnavailableError("replace unavailable")
    )
    blobs = FakeBlobRepository(upload_error=RepositoryUnavailableError("upload unavailable"))
    service = WorkItemService(records, blobs)
    pdf = validated_pdf()
    with pytest.raises(DependencyError):
        try:
            await service.create("owner-1", "request-key-123", pdf)
        finally:
            pdf.close()
    assert "Failed-state update after Blob upload failure failed." in caplog.messages
    assert next(iter(records.records.values())).status is WorkItemStatus.SUBMITTED


@pytest.mark.asyncio
async def test_owner_cannot_read_another_owners_record() -> None:
    record = work_item(owner_id="owner-2")
    records = FakeWorkItemRepository(records={record.id: record})
    service = WorkItemService(records, FakeBlobRepository())
    with pytest.raises(NotFoundError):
        await service.get("owner-1", record.id)


@pytest.mark.asyncio
async def test_queue_transition_failure_deletes_uploaded_blob() -> None:
    records = FakeWorkItemRepository(replace_error=RepositoryUnavailableError("unavailable"))
    blobs = FakeBlobRepository()
    service = WorkItemService(records, blobs)
    pdf = validated_pdf()
    with pytest.raises(DependencyError):
        try:
            await service.create("owner-1", "request-key-123", pdf)
        finally:
            pdf.close()
    assert blobs.blobs == {}


@pytest.mark.asyncio
async def test_blob_cleanup_failure_is_logged(caplog) -> None:
    class QueueFailureRepository(FakeWorkItemRepository):
        replace_calls = 0

        async def replace(self, record):
            self.replace_calls += 1
            if self.replace_calls == 1:
                raise RepositoryUnavailableError("queue unavailable")
            return await super().replace(record)

    records = QueueFailureRepository()
    blobs = FakeBlobRepository(delete_error=RepositoryError("delete failed"))
    service = WorkItemService(records, blobs)
    pdf = validated_pdf()
    with pytest.raises(DependencyError):
        try:
            await service.create("owner-1", "request-key-123", pdf)
        finally:
            pdf.close()
    assert "Blob compensation failed." in caplog.messages
    assert next(iter(records.records.values())).status is WorkItemStatus.FAILED


def test_deterministic_ids_are_owner_scoped() -> None:
    key_hash = idempotency_key_hash("request-key-123")
    assert deterministic_work_item_id("owner-1", key_hash) != (
        deterministic_work_item_id("owner-2", key_hash)
    )
