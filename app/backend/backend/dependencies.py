from __future__ import annotations

from dataclasses import dataclass

from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

from .config import Settings
from .repositories import (
    AzureBlobRepository,
    AzureWorkItemRepository,
    BlobRepository,
    WorkItemRepository,
)
from .services import WorkItemService


@dataclass(slots=True)
class AppDependencies:
    blob_repository: BlobRepository
    work_item_repository: WorkItemRepository
    work_item_service: WorkItemService
    credential: DefaultAzureCredential | None = None

    async def close(self) -> None:
        await self.blob_repository.close()
        await self.work_item_repository.close()
        if self.credential is not None:
            await self.credential.close()


def build_dependencies(settings: Settings) -> AppDependencies:
    credential = DefaultAzureCredential()
    blob_client = BlobServiceClient(
        account_url=settings.resolved_storage_endpoint,
        credential=credential,
    )
    cosmos_client = CosmosClient(
        url=settings.resolved_cosmos_endpoint,
        credential=credential,
    )
    blob_repository = AzureBlobRepository(blob_client, settings.storage_container)
    work_item_repository = AzureWorkItemRepository(
        cosmos_client,
        settings.cosmos_database,
        settings.cosmos_container,
    )
    return AppDependencies(
        blob_repository=blob_repository,
        work_item_repository=work_item_repository,
        work_item_service=WorkItemService(work_item_repository, blob_repository),
        credential=credential,
    )
