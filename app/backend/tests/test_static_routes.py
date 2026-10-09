from pathlib import Path

import pytest
from backend.app import create_app


@pytest.fixture
def static_directory(tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<main>starter frontend</main>")
    (tmp_path / "assets" / "app.js").write_text("console.info('starter')")
    return tmp_path


@pytest.mark.asyncio
async def test_root_and_frontend_routes_serve_spa(
    settings,
    dependencies,
    static_directory: Path,
) -> None:
    app = create_app(settings, dependencies, static_directory)
    async with app.test_app():
        client = app.test_client()
        root = await client.get("/")
        detail = await client.get("/work-items/example")
    assert root.status_code == 200
    assert detail.status_code == 200
    assert "starter frontend" in (await detail.get_data(as_text=True))


@pytest.mark.asyncio
async def test_static_asset_and_missing_asset_behavior(
    settings,
    dependencies,
    static_directory: Path,
) -> None:
    app = create_app(settings, dependencies, static_directory)
    async with app.test_app():
        client = app.test_client()
        asset = await client.get("/assets/app.js")
        missing = await client.get("/assets/missing.js")
    assert asset.status_code == 200
    assert missing.status_code == 404
    assert (await missing.get_json())["error"]["code"] == "http_error"


@pytest.mark.asyncio
async def test_unknown_api_route_is_not_spa_fallback(
    settings,
    dependencies,
    static_directory: Path,
) -> None:
    app = create_app(settings, dependencies, static_directory)
    async with app.test_app():
        response = await app.test_client().get("/api/v1/unknown")
    assert response.status_code == 404
    assert (await response.get_json())["error"]["code"] == "http_error"


@pytest.mark.asyncio
async def test_static_path_traversal_is_rejected(
    settings,
    dependencies,
    static_directory: Path,
) -> None:
    app = create_app(settings, dependencies, static_directory)
    async with app.test_app():
        response = await app.test_client().get("/assets/%2e%2e/secret.txt")
    assert response.status_code == 404
