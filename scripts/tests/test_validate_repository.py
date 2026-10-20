import json
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from scripts import validate_repository as validator


def test_working_files_exclude_deletions_and_deduplicate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "README.md").write_text("# Current\n", encoding="utf-8")
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(
            args=[], returncode=0, stdout="README.md\nremoved.md\nREADME.md\n", stderr=""
        ),
    )

    assert validator._tracked_files() == ["README.md"]


def test_missing_required_files_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "README.md").write_text("# Current\n", encoding="utf-8")
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    errors: list[str] = []

    validator._check_required_files(errors)

    assert "Missing required file: LICENSE" in errors
    assert "Missing required file: README.md" not in errors


@pytest.mark.parametrize(
    ("relative", "message"),
    [
        (".venv/lib/module.py", "Tracked local or generated path"),
        ("app/frontend/node_modules/pkg/index.js", "Tracked local or generated path"),
        ("app/backend/static/index.html", "Tracked generated artifact"),
        ("tests/sample-data/generated/hello-world.pdf", "Tracked generated artifact"),
        ("app/backend/.env", "Tracked environment file"),
        ("tests/sample-data/real.pdf", "Tracked generated sample PDF"),
    ],
)
def test_forbidden_tracked_files_fail(relative: str, message: str) -> None:
    errors: list[str] = []

    validator._check_tracked_files([relative], errors)

    assert any(message in error for error in errors)


@pytest.mark.parametrize(
    "relative",
    [
        "app/backend/.env.example",
        "app/backend/static/.gitkeep",
        "tests/sample-data/generated/.gitkeep",
        "docs/README.md",
    ],
)
def test_allowed_tracked_files_pass(relative: str) -> None:
    errors: list[str] = []

    validator._check_tracked_files([relative], errors)

    assert errors == []


def test_ai_service_contract_detects_mapping_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    infra = tmp_path / "infra"
    infra.mkdir()
    (infra / "main.parameters.json").write_text(
        json.dumps({"parameters": {"useFoundry": {"value": "${USE_FOUNDRY=none}"}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    errors: list[str] = []

    validator._check_ai_service_contract(errors)

    assert "Invalid optional AI service parameter mapping: useFoundry" in errors
    assert "Missing optional AI service contract file: infra/modules/ai/foundry.bicep" in errors


def test_repository_passes_current_policy() -> None:
    errors: list[str] = []

    validator._check_required_files(errors)
    validator._check_ai_service_contract(errors)

    assert errors == []
