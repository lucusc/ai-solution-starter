from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

import pytest
from backend.app import create_app
from backend.config import Settings
from backend.dependencies import AppDependencies
from backend.models import WorkItemRecord, WorkItemStatus
from backend.pdf import ValidatedPdf
from backend.repositories import (
    RepositoryConflictError,
    RepositoryError,
    WorkItemPage,
)
from backend.services import WorkItemService
from quart import Quart


@dataclass
class FakeBlobRepository:
    blobs: dict[str, bytes] = field(default_factory=dict)
    upload_error: RepositoryError | None = None
    delete_error: RepositoryError | None = None
    ready_value: bool = True

    async def upload_source(self, work_item_id: str, pdf: ValidatedPdf) -> str:
        if self.upload_error:
            raise self.upload_error
        name = f"work-items/{work_item_id}/source.pdf"
        if name in self.blobs:
            raise RepositoryConflictError("Blob exists.")
        pdf.stream.seek(0)
        self.blobs[name] = pdf.stream.read()
        return name

    async def delete_source(self, blob_name: str) -> None:
        if self.delete_error:
            raise self.delete_error
        self.blobs.pop(blob_name, None)

    async def ready(self) -> bool:
        return self.ready_value

    async def close(self) -> None:
        return None


@dataclass
class FakeWorkItemRepository:
    records: dict[str, WorkItemRecord] = field(default_factory=dict)
    create_error: RepositoryError | None = None
    replace_error: RepositoryError | None = None
    ready_value: bool = True

    async def create(self, record: WorkItemRecord) -> WorkItemRecord:
        if self.create_error:
            raise self.create_error
        if record.id in self.records:
            raise RepositoryConflictError("Record exists.")
        stored = record.model_copy(update={"etag": f"etag-{record.version}"})
        self.records[record.id] = stored
        return stored

    async def find_by_id(
        self,
        work_item_id: str,
        owner_id: str,
    ) -> WorkItemRecord | None:
        record = self.records.get(work_item_id)
        return record if record and record.owner_id == owner_id else None

    async def list_for_owner(
        self,
        owner_id: str,
        *,
        status: WorkItemStatus | None,
        page_size: int,
        continuation_token: str | None,
    ) -> WorkItemPage:
        records = [
            record
            for record in self.records.values()
            if record.owner_id == owner_id and (status is None or record.status == status)
        ]
        records.sort(key=lambda record: record.created_at, reverse=True)
        offset = int(continuation_token or "0")
        page = records[offset : offset + page_size]
        next_offset = offset + len(page)
        token = str(next_offset) if next_offset < len(records) else None
        return WorkItemPage(page, token)

    async def replace(self, record: WorkItemRecord) -> WorkItemRecord:
        if self.replace_error:
            raise self.replace_error
        if record.id not in self.records:
            raise RepositoryConflictError("Record missing.")
        stored = record.model_copy(update={"etag": f"etag-{record.version}"})
        self.records[record.id] = stored
        return stored

    async def delete(self, record: WorkItemRecord) -> None:
        self.records.pop(record.id, None)

    async def ready(self) -> bool:
        return self.ready_value

    async def close(self) -> None:
        return None


@pytest.fixture
def settings() -> Settings:
    return Settings(
        storage_account="starterstorage",
        storage_container="inputs",
        cosmos_account="startercosmos",
        cosmos_database="starter",
        cosmos_container="inputs",
        local_auth_subject="owner-1",
        readiness_cache_seconds=1,
    )


@pytest.fixture
def blob_repository() -> FakeBlobRepository:
    return FakeBlobRepository()


@pytest.fixture
def work_item_repository() -> FakeWorkItemRepository:
    return FakeWorkItemRepository()


@pytest.fixture
def dependencies(
    blob_repository: FakeBlobRepository,
    work_item_repository: FakeWorkItemRepository,
) -> AppDependencies:
    return AppDependencies(
        blob_repository=blob_repository,
        work_item_repository=work_item_repository,
        work_item_service=WorkItemService(work_item_repository, blob_repository),
    )


@pytest.fixture
def app(settings: Settings, dependencies: AppDependencies) -> Quart:
    return create_app(settings, dependencies)


@pytest.fixture
async def client(app: Quart) -> AsyncIterator[Any]:
    async with app.test_app():
        yield app.test_client()
