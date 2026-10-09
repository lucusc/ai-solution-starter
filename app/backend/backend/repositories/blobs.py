from __future__ import annotations

from typing import Protocol

from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient

from ..pdf import ValidatedPdf
from .errors import (
    RepositoryConflictError,
    RepositoryError,
    RepositoryUnavailableError,
)


class BlobRepository(Protocol):
    async def upload_source(self, work_item_id: str, pdf: ValidatedPdf) -> str: ...

    async def delete_source(self, blob_name: str) -> None: ...

    async def ready(self) -> bool: ...

    async def close(self) -> None: ...


def _map_http_error(exc: HttpResponseError) -> RepositoryError:
    if exc.status_code in {408, 429, 500, 502, 503, 504}:
        return RepositoryUnavailableError("Blob Storage is unavailable.")
    return RepositoryError("Blob Storage rejected the operation.")


class AzureBlobRepository:
    def __init__(
        self,
        service_client: BlobServiceClient,
        container_name: str,
    ) -> None:
        self._service_client = service_client
        self._container = service_client.get_container_client(container_name)

    async def upload_source(self, work_item_id: str, pdf: ValidatedPdf) -> str:
        blob_name = f"work-items/{work_item_id}/source.pdf"
        blob = self._container.get_blob_client(blob_name)
        pdf.stream.seek(0)
        try:
            await blob.upload_blob(
                pdf.stream,
                overwrite=False,
                content_settings=ContentSettings(content_type="application/pdf"),
                metadata={
                    "work_item_id": work_item_id,
                    "sha256": pdf.sha256,
                },
            )
        except ResourceExistsError as exc:
            raise RepositoryConflictError("The work-item blob already exists.") from exc
        except HttpResponseError as exc:
            raise _map_http_error(exc) from exc
        return blob_name

    async def delete_source(self, blob_name: str) -> None:
        try:
            await self._container.delete_blob(blob_name, delete_snapshots="include")
        except HttpResponseError as exc:
            if exc.status_code != 404:
                raise _map_http_error(exc) from exc

    async def ready(self) -> bool:
        try:
            await self._container.get_container_properties()
        except HttpResponseError as exc:
            raise _map_http_error(exc) from exc
        return True

    async def close(self) -> None:
        await self._service_client.close()
