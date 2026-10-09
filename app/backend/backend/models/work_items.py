from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkItemStatus(StrEnum):
    SUBMITTED = "submitted"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


TERMINAL_STATUSES = {WorkItemStatus.COMPLETED, WorkItemStatus.FAILED}

ALLOWED_TRANSITIONS: dict[WorkItemStatus, set[WorkItemStatus]] = {
    WorkItemStatus.SUBMITTED: {WorkItemStatus.QUEUED, WorkItemStatus.FAILED},
    WorkItemStatus.QUEUED: {WorkItemStatus.PROCESSING, WorkItemStatus.FAILED},
    WorkItemStatus.PROCESSING: {
        WorkItemStatus.COMPLETED,
        WorkItemStatus.FAILED,
    },
    WorkItemStatus.COMPLETED: set(),
    WorkItemStatus.FAILED: set(),
}


def utc_now() -> datetime:
    return datetime.now(UTC)


class StoredSource(BaseModel):
    blob_name: str
    content_type: str = "application/pdf"
    size_bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class PublicSource(BaseModel):
    name: str
    content_type: str
    size_bytes: int
    sha256: str


class ProcessingError(BaseModel):
    code: str
    message: str
    retryable: bool
    occurred_at: datetime


class WorkItemRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    created_at: datetime
    updated_at: datetime
    owner_id: str
    status: WorkItemStatus
    version: int = Field(ge=1)
    source_name: str
    source: StoredSource
    idempotency_key_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    result: dict[str, Any] | None = None
    error: ProcessingError | None = None
    etag: str | None = Field(default=None, alias="_etag")

    def to_document(self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            by_alias=True,
            exclude={"etag"},
            exclude_none=False,
        )

    def transition(
        self,
        status: WorkItemStatus,
        *,
        error: ProcessingError | None = None,
        result: dict[str, Any] | None = None,
        now: datetime | None = None,
    ) -> WorkItemRecord:
        if status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(f"Invalid work-item transition from {self.status} to {status}.")
        if status is WorkItemStatus.FAILED and error is None:
            raise ValueError("Failed work items require an error.")
        if status is WorkItemStatus.COMPLETED and result is None:
            raise ValueError("Completed work items require a result.")
        return self.model_copy(
            update={
                "status": status,
                "error": error,
                "result": result,
                "updated_at": now or utc_now(),
                "version": self.version + 1,
            }
        )


class WorkItemResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    status: WorkItemStatus
    version: int
    source: PublicSource
    result: dict[str, Any] | None
    error: ProcessingError | None

    @classmethod
    def from_record(cls, record: WorkItemRecord) -> WorkItemResponse:
        return cls(
            id=record.id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            status=record.status,
            version=record.version,
            source=PublicSource(
                name=record.source_name,
                content_type=record.source.content_type,
                size_bytes=record.source.size_bytes,
                sha256=record.source.sha256,
            ),
            result=record.result,
            error=record.error,
        )


class WorkItemStatusResponse(BaseModel):
    id: str
    status: WorkItemStatus
    updated_at: datetime
    error: ProcessingError | None

    @classmethod
    def from_record(cls, record: WorkItemRecord) -> WorkItemStatusResponse:
        return cls(
            id=record.id,
            status=record.status,
            updated_at=record.updated_at,
            error=record.error,
        )


class WorkItemListResponse(BaseModel):
    items: list[WorkItemResponse]
    continuation_token: str | None
