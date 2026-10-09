import pytest


@pytest.mark.asyncio
async def test_health_is_anonymous(client) -> None:
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert await response.get_json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_readiness_is_anonymous(client) -> None:
    response = await client.get("/readyz")
    assert response.status_code == 200
    assert await response.get_json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_failed_readiness_is_cached(
    client,
    blob_repository,
    work_item_repository,
) -> None:
    blob_repository.ready_value = False
    first = await client.get("/readyz")
    blob_repository.ready_value = True
    work_item_repository.ready_value = True
    second = await client.get("/readyz")
    assert first.status_code == 503
    assert second.status_code == 503
    assert await second.get_json() == {"status": "not_ready"}
