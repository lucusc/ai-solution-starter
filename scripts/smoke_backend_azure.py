#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path
from tempfile import SpooledTemporaryFile

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "app" / "backend"))
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

from backend.config import Settings  # noqa: E402
from backend.dependencies import build_dependencies  # noqa: E402
from backend.models import WorkItemStatus  # noqa: E402
from backend.pdf import ValidatedPdf  # noqa: E402
from backend.services.work_items import (  # noqa: E402
    deterministic_work_item_id,
    idempotency_key_hash,
)
from load_azd_env import load_azd_env  # noqa: E402


def _default_environment() -> str:
    result = subprocess.run(
        ["azd", "env", "list", "-o", "json"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
    )
    environments = json.loads(result.stdout)
    selected = next(
        (item["Name"] for item in environments if item.get("IsDefault")),
        None,
    )
    if not selected:
        raise RuntimeError("No default azd environment is selected.")
    return str(selected)


def _synthetic_pdf(label: str) -> ValidatedPdf:
    content = f"%PDF-1.4\n% synthetic {label}\n%%EOF\n".encode()
    stream = SpooledTemporaryFile(max_size=1024, mode="w+b")
    stream.write(content)
    stream.seek(0)
    return ValidatedPdf(
        stream=stream,
        display_name=f"{label}.pdf",
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
    )


async def _run(environment: str) -> None:
    if _default_environment() != environment:
        raise RuntimeError("The requested environment is not the selected default azd environment.")
    load_azd_env()
    settings = Settings.from_environment()
    dependencies = build_dependencies(settings)
    owner_id = f"smoke-{uuid.uuid4()}"
    other_owner_id = f"smoke-{uuid.uuid4()}"
    cleanup_targets: list[tuple[str, str, str]] = []
    owner_item_ids: list[str] = []
    try:
        for index, current_owner in enumerate([owner_id, owner_id, other_owner_id]):
            pdf = _synthetic_pdf(f"smoke-{index}")
            key = f"smoke-key-{uuid.uuid4()}"
            item_id = deterministic_work_item_id(
                current_owner,
                idempotency_key_hash(key),
            )
            cleanup_targets.append((current_owner, item_id, f"work-items/{item_id}/source.pdf"))
            if current_owner == owner_id:
                owner_item_ids.append(item_id)
            try:
                created = await dependencies.work_item_service.create(
                    current_owner,
                    key,
                    pdf,
                )
                replay = await dependencies.work_item_service.create(
                    current_owner,
                    key,
                    pdf,
                )
                if not replay.replayed or replay.record.id != created.record.id:
                    raise RuntimeError("Idempotency replay validation failed.")
            finally:
                pdf.close()

        first_page = await dependencies.work_item_service.list(
            owner_id,
            status=WorkItemStatus.QUEUED,
            page_size=1,
            continuation_token=None,
        )
        if [item.id for item in first_page.items] != [
            owner_item_ids[1]
        ] or not first_page.continuation_token:
            raise RuntimeError("First continuation page validation failed.")
        second_page = await dependencies.work_item_service.list(
            owner_id,
            status=WorkItemStatus.QUEUED,
            page_size=1,
            continuation_token=first_page.continuation_token,
        )
        if [item.id for item in second_page.items] != [
            owner_item_ids[0]
        ] or second_page.continuation_token is not None:
            raise RuntimeError("Second continuation page validation failed.")
        empty_status_page = await dependencies.work_item_service.list(
            owner_id,
            status=WorkItemStatus.PROCESSING,
            page_size=1,
            continuation_token=None,
        )
        if empty_status_page.items:
            raise RuntimeError("Status filtering validation failed.")
        print("Live backend repository smoke test passed.")
    finally:
        cleanup_errors: list[Exception] = []
        for current_owner, item_id, blob_name in cleanup_targets:
            try:
                await dependencies.blob_repository.delete_source(blob_name)
            except Exception as exc:
                cleanup_errors.append(exc)
                print(f"Blob cleanup failed for work item {item_id}: {exc}", file=sys.stderr)
            try:
                record = await dependencies.work_item_repository.find_by_id(
                    item_id,
                    current_owner,
                )
                if record is not None:
                    await dependencies.work_item_repository.delete(record)
            except Exception as exc:
                cleanup_errors.append(exc)
                print(
                    f"Cosmos cleanup failed for work item {item_id}: {exc}",
                    file=sys.stderr,
                )
        try:
            await dependencies.close()
        except Exception as exc:
            cleanup_errors.append(exc)
            print(f"Dependency shutdown failed: {exc}", file=sys.stderr)
        if cleanup_errors and sys.exception() is None:
            raise RuntimeError("Live smoke cleanup did not complete.") from cleanup_errors[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run opt-in Blob Storage and Cosmos DB backend smoke checks."
    )
    parser.add_argument("--environment", required=True)
    parser.add_argument(
        "--confirm-environment",
        required=True,
        help="Must exactly match --environment.",
    )
    args = parser.parse_args()
    if args.environment != args.confirm_environment:
        raise SystemExit("Environment confirmation does not match.")
    asyncio.run(_run(args.environment))


if __name__ == "__main__":
    main()
