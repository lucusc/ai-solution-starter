from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from quart import Blueprint, current_app, jsonify

from ..dependencies import AppDependencies

health_blueprint = Blueprint("health", __name__)


@health_blueprint.get("/healthz")
async def health() -> tuple[Any, int]:
    return jsonify({"status": "healthy"}), 200


@health_blueprint.get("/readyz")
async def readiness() -> tuple[Any, int]:
    settings = current_app.extensions["settings"]
    cache: dict[str, Any] = current_app.extensions["readiness_cache"]
    now = datetime.now(UTC)
    expires_at = cache.get("expires_at")
    if isinstance(expires_at, datetime) and expires_at > now:
        ready = bool(cache.get("ready"))
        return jsonify({"status": "ready" if ready else "not_ready"}), (200 if ready else 503)

    dependencies: AppDependencies = current_app.extensions["dependencies"]
    ready = False
    try:
        blob_ready, cosmos_ready = await asyncio.wait_for(
            asyncio.gather(
                dependencies.blob_repository.ready(),
                dependencies.work_item_repository.ready(),
            ),
            timeout=5,
        )
        ready = blob_ready and cosmos_ready
    except Exception:
        current_app.logger.exception("Readiness dependency check failed.")

    cache["ready"] = ready
    cache["expires_at"] = now + timedelta(seconds=settings.readiness_cache_seconds)
    return jsonify({"status": "ready" if ready else "not_ready"}), (200 if ready else 503)
