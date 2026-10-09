from datetime import UTC, datetime

import pytest
from backend.models import ProcessingError, WorkItemResponse, WorkItemStatus

from tests.helpers import work_item


def test_public_response_excludes_internal_fields() -> None:
    response = WorkItemResponse.from_record(work_item())
    serialized = response.model_dump(mode="json")
    assert "owner_id" not in serialized
    assert "idempotency_key_hash" not in serialized
    assert "blob_name" not in serialized["source"]


def test_invalid_terminal_transition_is_rejected() -> None:
    record = work_item(status=WorkItemStatus.COMPLETED)
    with pytest.raises(ValueError):
        record.transition(WorkItemStatus.FAILED)


def test_failed_transition_requires_structured_error() -> None:
    record = work_item(status=WorkItemStatus.QUEUED)
    failed = record.transition(
        WorkItemStatus.FAILED,
        error=ProcessingError(
            code="processing_failed",
            message="Processing failed.",
            retryable=False,
            occurred_at=datetime.now(UTC),
        ),
    )
    assert failed.version == record.version + 1
    assert failed.status is WorkItemStatus.FAILED
