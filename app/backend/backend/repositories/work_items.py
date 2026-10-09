from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from azure.core import MatchConditions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)

from ..models import WorkItemRecord, WorkItemStatus
from .errors import (
    RepositoryConflictError,
    RepositoryError,
    RepositoryUnavailableError,
)


@dataclass(frozen=True, slots=True)
class WorkItemPage:
    items: list[WorkItemRecord]
    continuation_token: str | None


class WorkItemRepository(Protocol):
    async def create(self, record: WorkItemRecord) -> WorkItemRecord: ...

    async def find_by_id(
        self,
        work_item_id: str,
        owner_id: str,
    ) -> WorkItemRecord | None: ...

    async def list_for_owner(
        self,
        owner_id: str,
        *,
        status: WorkItemStatus | None,
        page_size: int,
        continuation_token: str | None,
    ) -> WorkItemPage: ...

    async def replace(self, record: WorkItemRecord) -> WorkItemRecord: ...

    async def delete(self, record: WorkItemRecord) -> None: ...

    async def ready(self) -> bool: ...

    async def close(self) -> None: ...


def _map_cosmos_error(exc: CosmosHttpResponseError) -> RepositoryError:
    if exc.status_code in {408, 429, 500, 502, 503, 504}:
        return RepositoryUnavailableError("Cosmos DB is unavailable.")
    return RepositoryError("Cosmos DB rejected the operation.")


class AzureWorkItemRepository:
    def __init__(
        self,
        client: CosmosClient,
        database_name: str,
        container_name: str,
    ) -> None:
        self._client = client
        self._database = client.get_database_client(database_name)
        self._container = self._database.get_container_client(container_name)

    async def create(self, record: WorkItemRecord) -> WorkItemRecord:
        try:
            created = await self._container.create_item(body=record.to_document())
        except CosmosResourceExistsError as exc:
            raise RepositoryConflictError("The work item already exists.") from exc
        except CosmosHttpResponseError as exc:
            raise _map_cosmos_error(exc) from exc
        return WorkItemRecord.model_validate(created)

    async def find_by_id(
        self,
        work_item_id: str,
        owner_id: str,
    ) -> WorkItemRecord | None:
        query = "SELECT TOP 1 * FROM c WHERE c.id = @id AND c.owner_id = @owner_id"
        parameters: list[dict[str, object]] = [
            {"name": "@id", "value": work_item_id},
            {"name": "@owner_id", "value": owner_id},
        ]
        try:
            items = self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
                enable_scan_in_query=True,
                max_item_count=1,
            )
            async for item in items:
                return WorkItemRecord.model_validate(item)
        except CosmosHttpResponseError as exc:
            raise _map_cosmos_error(exc) from exc
        return None

    async def list_for_owner(
        self,
        owner_id: str,
        *,
        status: WorkItemStatus | None,
        page_size: int,
        continuation_token: str | None,
    ) -> WorkItemPage:
        clauses = ["c.owner_id = @owner_id"]
        parameters: list[dict[str, Any]] = [{"name": "@owner_id", "value": owner_id}]
        if status is not None:
            clauses.append("c.status = @status")
            parameters.append({"name": "@status", "value": status.value})
        query = f"SELECT * FROM c WHERE {' AND '.join(clauses)} ORDER BY c.created_at DESC"
        try:
            items = self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
                enable_scan_in_query=True,
                max_item_count=page_size,
            )
            pages: Any = items.by_page(continuation_token=continuation_token)
            try:
                page = await anext(pages)
            except StopAsyncIteration:
                return WorkItemPage(items=[], continuation_token=None)
            records = [WorkItemRecord.model_validate(item) async for item in page]
            return WorkItemPage(
                items=records,
                continuation_token=pages.continuation_token,
            )
        except CosmosHttpResponseError as exc:
            raise _map_cosmos_error(exc) from exc

    async def replace(self, record: WorkItemRecord) -> WorkItemRecord:
        kwargs: dict[str, Any] = {}
        if record.etag:
            kwargs["etag"] = record.etag
            kwargs["match_condition"] = MatchConditions.IfNotModified
        try:
            replaced = await self._container.replace_item(
                item=record.id,
                body=record.to_document(),
                **kwargs,
            )
        except CosmosResourceNotFoundError as exc:
            raise RepositoryConflictError("The work item no longer exists.") from exc
        except CosmosHttpResponseError as exc:
            if exc.status_code in {409, 412}:
                raise RepositoryConflictError("The work item changed during the update.") from exc
            raise _map_cosmos_error(exc) from exc
        return WorkItemRecord.model_validate(replaced)

    async def delete(self, record: WorkItemRecord) -> None:
        try:
            await self._container.delete_item(
                item=record.id,
                partition_key=record.created_at.isoformat().replace("+00:00", "Z"),
            )
        except CosmosResourceNotFoundError:
            return
        except CosmosHttpResponseError as exc:
            raise _map_cosmos_error(exc) from exc

    async def ready(self) -> bool:
        try:
            await self._container.read()
        except CosmosHttpResponseError as exc:
            raise _map_cosmos_error(exc) from exc
        return True

    async def close(self) -> None:
        await self._client.close()
