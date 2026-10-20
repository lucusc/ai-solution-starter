#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "docs/README.md",
}
FORBIDDEN_PARTS = {
    ".azure",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".source-staging",
    ".venv",
    "__pycache__",
    "node_modules",
}
FORBIDDEN_PREFIXES = (
    "app/backend/static/",
    "tests/sample-data/generated/",
)


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        line
        for line in dict.fromkeys(result.stdout.splitlines())
        if line and (REPO_ROOT / line).is_file()
    ]


def _check_required_files(errors: list[str]) -> None:
    for relative in sorted(REQUIRED_FILES):
        if not (REPO_ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative}")


def _check_tracked_files(tracked: list[str], errors: list[str]) -> None:
    for relative in tracked:
        path = Path(relative)
        if FORBIDDEN_PARTS.intersection(path.parts):
            errors.append(f"Tracked local or generated path: {relative}")
        if relative.startswith(FORBIDDEN_PREFIXES) and path.name != ".gitkeep":
            errors.append(f"Tracked generated artifact: {relative}")
        if path.name.startswith(".env") and path.name != ".env.example":
            errors.append(f"Tracked environment file: {relative}")
        if path.suffix.lower() == ".pdf" and relative.startswith("tests/sample-data/"):
            errors.append(f"Tracked generated sample PDF: {relative}")


def _check_ai_service_contract(errors: list[str]) -> None:
    parameters_path = REPO_ROOT / "infra" / "main.parameters.json"
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))["parameters"]
    expected = {
        "useFoundry": "${USE_FOUNDRY=new}",
        "useOpenAi": "${USE_OPENAI=none}",
        "useDocumentIntelligence": "${USE_DOCUMENT_INTELLIGENCE=none}",
        "existingOpenAiResourceId": "${EXISTING_OPENAI_RESOURCE_ID}",
        "deployOpenAiModelsExisting": "${DEPLOY_OPENAI_MODELS_EXISTING=false}",
        "foundryAccountResourceId": "${EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID}",
        "foundryProjectResourceId": "${EXISTING_FOUNDRY_PROJECT_RESOURCE_ID}",
        "foundryModelDeploymentName": "${AZURE_FOUNDRY_MODEL_DEPLOYMENT=starter-gpt-4o}",
        "documentIntelligenceResourceId": "${EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID}",
        "configureExistingAiServices": "${CONFIGURE_EXISTING_AI_SERVICES=false}",
        "deployFoundryModelExisting": "${DEPLOY_FOUNDRY_MODEL_EXISTING=false}",
    }
    for parameter, value in expected.items():
        if parameters.get(parameter, {}).get("value") != value:
            errors.append(f"Invalid optional AI service parameter mapping: {parameter}")

    for relative in (
        "infra/modules/ai/foundry.bicep",
        "infra/modules/ai/document-intelligence.bicep",
        "scripts/validate_ai_service_config.py",
    ):
        if not (REPO_ROOT / relative).is_file():
            errors.append(f"Missing optional AI service contract file: {relative}")


def main() -> int:
    errors: list[str] = []
    tracked = _tracked_files()
    _check_required_files(errors)
    _check_tracked_files(tracked, errors)
    _check_ai_service_contract(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Repository validation passed ({len(tracked)} working-tree files checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
