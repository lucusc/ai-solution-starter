from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass

from ..errors import ConflictError, DependencyError, NotFoundError
from ..models import (
    ProcessingError,
    StoredSource,
    WorkItemRecord,
    WorkItemStatus,
    utc_now,
)
from ..pdf import ValidatedPdf
from ..repositories import (
    BlobRepository,
    RepositoryConflictError,
    RepositoryError,
    RepositoryUnavailableError,
    WorkItemPage,
    WorkItemRepository,
)

logger = logging.getLogger(__name__)

WORK_ITEM_NAMESPACE = uuid.UUID("0cbe8939-c72f-4648-9ad2-901c98aa0d0b")
MIN_IDEMPOTENCY_KEY_LENGTH = 8
MAX_IDEMPOTENCY_KEY_LENGTH = 128


@dataclass(frozen=True, slots=True)
class CreateWorkItemResult:
    record: WorkItemRecord
    replayed: bool


def idempotency_key_hash(key: str) -> str:
    if not MIN_IDEMPOTENCY_KEY_LENGTH <= len(key) <= MAX_IDEMPOTENCY_KEY_LENGTH:
        raise ValueError("Idempotency-Key must be between 8 and 128 characters.")
    if any(ord(character) < 33 or ord(character) > 126 for character in key):
        raise ValueError("Idempotency-Key must contain visible ASCII characters.")
    return hashlib.sha256(key.encode("ascii")).hexdigest()


def deterministic_work_item_id(owner_id: str, key_hash: str) -> str:
    return str(uuid.uuid5(WORK_ITEM_NAMESPACE, f"{owner_id}:{key_hash}"))


def _dependency_error(exc: RepositoryError, operation: str) -> DependencyError:
    return DependencyError(
        f"{operation}_failed",
        "A required Azure service could not complete the request.",
        unavailable=isinstance(exc, RepositoryUnavailableError),
    )


class WorkItemService:
    def __init__(
        self,
        work_items: WorkItemRepository,
        blobs: BlobRepository,
    ) -> None:
        self._work_items = work_items
        self._blobs = blobs

    async def create(
        self,
        owner_id: str,
        idempotency_key: str,
        pdf: ValidatedPdf,
    ) -> CreateWorkItemResult:
        key_hash = idempotency_key_hash(idempotency_key)
        work_item_id = deterministic_work_item_id(owner_id, key_hash)
        existing = await self._find_for_replay(work_item_id, owner_id, key_hash)
        if existing is not None:
            return CreateWorkItemResult(record=existing, replayed=True)

        now = utc_now()
        blob_name = f"work-items/{work_item_id}/source.pdf"
        submitted = WorkItemRecord(
            id=work_item_id,
            created_at=now,
            updated_at=now,
            owner_id=owner_id,
            status=WorkItemStatus.SUBMITTED,
            version=1,
            source_name=pdf.display_name,
            source=StoredSource(
                blob_name=blob_name,
                size_bytes=pdf.size_bytes,
                sha256=pdf.sha256,
            ),
            idempotency_key_hash=key_hash,
        )
        try:
            submitted = await self._work_items.create(submitted)
        except RepositoryConflictError as exc:
            replay = await self._find_for_replay(work_item_id, owner_id, key_hash)
            if replay is not None:
                return CreateWorkItemResult(record=replay, replayed=True)
            raise ConflictError("The idempotent work item could not be resolved.") from exc
        except RepositoryError as exc:
            raise _dependency_error(exc, "work_item_create") from exc

        try:
            actual_blob_name = await self._blobs.upload_source(work_item_id, pdf)
            if actual_blob_name != blob_name:
                raise RepositoryError("Blob Storage returned an unexpected path.")
        except RepositoryError as exc:
            try:
                await self._mark_failed(
                    submitted,
                    code="blob_upload_failed",
                    message="The source file could not be stored.",
                    retryable=isinstance(exc, RepositoryUnavailableError),
                )
            except DependencyError:
                logger.exception(
                    "Failed-state update after Blob upload failure failed.",
                    extra={"work_item_id": work_item_id},
                )
                logger.error(
                    "Blob upload failed before failed-state compensation.",
                    exc_info=(type(exc), exc, exc.__traceback__),
                    extra={"work_item_id": work_item_id},
                )
            raise _dependency_error(exc, "blob_upload") from exc

        queued = submitted.transition(WorkItemStatus.QUEUED)
        try:
            queued = await self._work_items.replace(queued)
        except RepositoryError as exc:
            cleanup_failures: list[Exception] = []
            try:
                await self._blobs.delete_source(blob_name)
            except RepositoryError as cleanup_exc:
                cleanup_failures.append(cleanup_exc)
                logger.exception(
                    "Blob compensation failed.",
                    extra={"work_item_id": work_item_id},
                )
            try:
                await self._mark_failed(
                    submitted,
                    code="queue_transition_failed",
                    message="The work item could not be queued.",
                    retryable=isinstance(exc, RepositoryUnavailableError),
                )
            except DependencyError as cleanup_exc:
                cleanup_failures.append(cleanup_exc)
                logger.exception(
                    "Failed-state compensation failed.",
                    extra={"work_item_id": work_item_id},
                )
            if cleanup_failures:
                logger.error(
                    "Work-item compensation completed with failures.",
                    extra={
                        "work_item_id": work_item_id,
                        "cleanup_failure_count": len(cleanup_failures),
                    },
                )
            raise _dependency_error(exc, "queue_transition") from exc

        logger.info(
            "Work item queued.",
            extra={"work_item_id": work_item_id, "work_item_status": queued.status},
        )
        return CreateWorkItemResult(record=queued, replayed=False)

    async def _find_for_replay(
        self,
        work_item_id: str,
        owner_id: str,
        key_hash: str,
    ) -> WorkItemRecord | None:
        try:
            existing = await self._work_items.find_by_id(work_item_id, owner_id)
        except RepositoryError as exc:
            raise _dependency_error(exc, "idempotency_lookup") from exc
        if existing and existing.idempotency_key_hash != key_hash:
            raise ConflictError("The idempotency record is inconsistent.")
        return existing

    async def _mark_failed(
        self,
        record: WorkItemRecord,
        *,
        code: str,
        message: str,
        retryable: bool,
    ) -> WorkItemRecord:
        failed = record.transition(
            WorkItemStatus.FAILED,
            error=ProcessingError(
                code=code,
                message=message,
                retryable=retryable,
                occurred_at=utc_now(),
            ),
        )
        try:
            return await self._work_items.replace(failed)
        except RepositoryError as exc:
            raise _dependency_error(exc, "failed_status_update") from exc

    async def list(
        self,
        owner_id: str,
        *,
        status: WorkItemStatus | None,
        page_size: int,
        continuation_token: str | None,
    ) -> WorkItemPage:
        try:
            return await self._work_items.list_for_owner(
                owner_id,
                status=status,
                page_size=page_size,
                continuation_token=continuation_token,
            )
        except RepositoryError as exc:
            raise _dependency_error(exc, "work_item_list") from exc

    async def get(self, owner_id: str, work_item_id: str) -> WorkItemRecord:
        try:
            record = await self._work_items.find_by_id(work_item_id, owner_id)
        except RepositoryError as exc:
            raise _dependency_error(exc, "work_item_read") from exc
        if record is None:
            raise NotFoundError()
        return record
