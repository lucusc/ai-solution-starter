from __future__ import annotations

import json

from scripts.verify_logic_app_package import (
    PACKAGE,
    ROOT,
    is_canonical_work_item_path,
    validate_package,
)

FIXTURES = ROOT / "app" / "agent" / "tests" / "fixtures"


def test_logic_app_package_satisfies_foundry_contract() -> None:
    assert validate_package() == []


def test_blob_paths_require_canonical_work_item_uuid() -> None:
    trigger = json.loads((FIXTURES / "blob-trigger.json").read_text())
    path = trigger["path"]
    assert is_canonical_work_item_path(path)
    assert not is_canonical_work_item_path("work-items/not-a-uuid/source.pdf")
    assert not is_canonical_work_item_path(path.replace("source.pdf", "other.pdf"))
    assert not is_canonical_work_item_path(f"{path}/extra")


def test_queued_fixture_matches_blob_and_cosmos_contract() -> None:
    trigger = json.loads((FIXTURES / "blob-trigger.json").read_text())
    record = json.loads((FIXTURES / "queued-work-item.json").read_text())
    assert record["id"] == trigger["path"].split("/")[1]
    assert record["source"]["blob_name"] == trigger["path"]
    assert record["source"]["content_type"] == "application/pdf"
    assert record["status"] == "queued"
    assert record["created_at"]
    assert record["_etag"]


def test_foundry_fixtures_include_valid_and_invalid_structured_outputs() -> None:
    good = json.loads((FIXTURES / "foundry-success.json").read_text())
    bad = json.loads((FIXTURES / "foundry-invalid-output.json").read_text())
    assert json.loads(good["output_text"])["category"] == "informational"
    invalid = json.loads(bad["output_text"])
    assert invalid["category"] not in {
        "informational",
        "action_required",
        "reference",
        "other",
    }
    assert "owner_id" in invalid
    assert (PACKAGE / "process-document" / "workflow.json").is_file()


def test_synthetic_pdf_fixture_is_not_empty_or_over_the_backend_limit() -> None:
    pdf = (FIXTURES / "synthetic.pdf").read_bytes()
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) <= 20 * 1024 * 1024
