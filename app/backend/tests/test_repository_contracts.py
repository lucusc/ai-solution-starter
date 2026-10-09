from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from backend.config import Settings
from backend.dependencies import build_dependencies
from backend.models import WorkItemStatus
from backend.repositories.blobs import AzureBlobRepository
from backend.repositories.work_items import AzureWorkItemRepository

from tests.helpers import validated_pdf, work_item


@pytest.mark.asyncio
async def test_blob_upload_disables_overwrite() -> None:
    blob_client = SimpleNamespace(upload_blob=AsyncMock())
    container = SimpleNamespace(get_blob_client=MagicMock(return_value=blob_client))
    service = SimpleNamespace(get_container_client=MagicMock(return_value=container))
    repository = AzureBlobRepository(service, "inputs")  # type: ignore[arg-type]
    pdf = validated_pdf()
    try:
        await repository.upload_source("item-id", pdf)
    finally:
        pdf.close()
    assert blob_client.upload_blob.await_args.kwargs["overwrite"] is False


@pytest.mark.asyncio
async def test_cosmos_lookup_is_owner_scoped_and_scan_enabled() -> None:
    async def empty_items():
        if False:
            yield {}

    container = SimpleNamespace(query_items=MagicMock(return_value=empty_items()))
    database = SimpleNamespace(get_container_client=MagicMock(return_value=container))
    client = SimpleNamespace(get_database_client=MagicMock(return_value=database))
    repository = AzureWorkItemRepository(client, "starter", "inputs")  # type: ignore[arg-type]
    result = await repository.find_by_id("item-id", "owner-id")
    assert result is None
    call = container.query_items.call_args
    assert "c.owner_id = @owner_id" in call.kwargs["query"]
    assert call.kwargs["enable_cross_partition_query"] is True
    assert call.kwargs["enable_scan_in_query"] is True


@pytest.mark.asyncio
async def test_cosmos_list_passes_page_size_and_continuation_token() -> None:
    record = work_item()

    class Page:
        def __aiter__(self):
            self._items = iter([record.to_document()])
            return self

        async def __anext__(self):
            try:
                return next(self._items)
            except StopIteration as exc:
                raise StopAsyncIteration from exc

    class Pages:
        continuation_token = "next-token"

        def __aiter__(self):
            return self

        async def __anext__(self):
            return Page()

    pages = Pages()
    items = SimpleNamespace(by_page=MagicMock(return_value=pages))
    container = SimpleNamespace(query_items=MagicMock(return_value=items))
    database = SimpleNamespace(get_container_client=MagicMock(return_value=container))
    client = SimpleNamespace(get_database_client=MagicMock(return_value=database))
    repository = AzureWorkItemRepository(client, "starter", "inputs")  # type: ignore[arg-type]
    result = await repository.list_for_owner(
        "owner-1",
        status=WorkItemStatus.QUEUED,
        page_size=7,
        continuation_token="current-token",
    )
    assert [item.id for item in result.items] == [record.id]
    assert result.continuation_token == "next-token"
    assert container.query_items.call_args.kwargs["max_item_count"] == 7
    items.by_page.assert_called_once_with(continuation_token="current-token")


@pytest.mark.asyncio
async def test_cosmos_replace_uses_optimistic_concurrency() -> None:
    record = work_item().model_copy(update={"etag": "current-etag"})
    container = SimpleNamespace(replace_item=AsyncMock(return_value=record.to_document()))
    database = SimpleNamespace(get_container_client=MagicMock(return_value=container))
    client = SimpleNamespace(get_database_client=MagicMock(return_value=database))
    repository = AzureWorkItemRepository(client, "starter", "inputs")  # type: ignore[arg-type]
    await repository.replace(record)
    call = container.replace_item.await_args
    assert call.kwargs["etag"] == "current-etag"
    assert call.kwargs["match_condition"] is MatchConditions.IfNotModified


def test_dependency_builder_uses_token_credential_and_expected_endpoints(
    monkeypatch,
) -> None:
    credential = object()
    blob_client = SimpleNamespace(get_container_client=MagicMock(return_value=SimpleNamespace()))
    cosmos_client = SimpleNamespace(
        get_database_client=MagicMock(
            return_value=SimpleNamespace(
                get_container_client=MagicMock(return_value=SimpleNamespace())
            )
        )
    )
    credential_factory = MagicMock(return_value=credential)
    blob_factory = MagicMock(return_value=blob_client)
    cosmos_factory = MagicMock(return_value=cosmos_client)
    monkeypatch.setattr("backend.dependencies.DefaultAzureCredential", credential_factory)
    monkeypatch.setattr("backend.dependencies.BlobServiceClient", blob_factory)
    monkeypatch.setattr("backend.dependencies.CosmosClient", cosmos_factory)
    settings = Settings(
        storage_account="starterstorage",
        storage_container="inputs",
        cosmos_account="startercosmos",
        cosmos_database="starter",
        cosmos_container="inputs",
    )
    dependencies = build_dependencies(settings)
    assert dependencies.credential is credential
    blob_factory.assert_called_once_with(
        account_url="https://starterstorage.blob.core.windows.net",
        credential=credential,
    )
    cosmos_factory.assert_called_once_with(
        url="https://startercosmos.documents.azure.com:443/",
        credential=credential,
    )
