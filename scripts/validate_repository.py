#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "SUPPORT.md",
    "CODE_OF_CONDUCT.md",
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
    return [line for line in result.stdout.splitlines() if line]


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


def _link_target(markdown: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = unquote(target.split("#", 1)[0])
    if not target:
        return None
    return (markdown.parent / target).resolve()


def _check_markdown_links(tracked: list[str], errors: list[str]) -> None:
    root = REPO_ROOT.resolve()
    for relative in tracked:
        if not relative.endswith(".md"):
            continue
        markdown = REPO_ROOT / relative
        content = markdown.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(content):
            target = _link_target(markdown, match.group(1))
            if target is None:
                continue
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"{relative}: link escapes repository: {match.group(1)}")
                continue
            if not target.exists():
                errors.append(f"{relative}: missing link target: {match.group(1)}")


def _check_component_status(errors: list[str]) -> None:
    workflow_definitions = list(
        (REPO_ROOT / "app" / "agent" / "workflows").glob("**/workflow.json")
    )
    workflow_report = REPO_ROOT / "docs" / "reviews" / "PHASE_4_IMPLEMENTATION_REPORT.md"
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8").lower()

    if workflow_definitions and not workflow_report.is_file():
        errors.append("Logic App workflow exists without a Phase 4 implementation report.")
    if not workflow_definitions and "logic app" in readme and "not implemented" not in readme:
        errors.append("README must state that the Logic App workflow is not implemented.")


def _check_ai_service_contract(errors: list[str]) -> None:
    parameters_path = REPO_ROOT / "infra" / "main.parameters.json"
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))["parameters"]
    expected = {
        "useFoundry": "${USE_FOUNDRY=none}",
        "useDocumentIntelligence": "${USE_DOCUMENT_INTELLIGENCE=none}",
        "foundryAccountResourceId": "${EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID}",
        "foundryProjectResourceId": "${EXISTING_FOUNDRY_PROJECT_RESOURCE_ID}",
        "documentIntelligenceResourceId": "${EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID}",
        "configureExistingAiServices": "${CONFIGURE_EXISTING_AI_SERVICES=false}",
    }
    for parameter, value in expected.items():
        if parameters.get(parameter, {}).get("value") != value:
            errors.append(f"Invalid optional AI service parameter mapping: {parameter}")

    for relative in (
        "infra/modules/ai/foundry.bicep",
        "infra/modules/ai/document-intelligence.bicep",
        "docs/infrastructure/AI_SERVICES.md",
        "scripts/validate_ai_service_config.py",
    ):
        if not (REPO_ROOT / relative).is_file():
            errors.append(f"Missing optional AI service contract file: {relative}")


def main() -> int:
    errors: list[str] = []
    tracked = _tracked_files()
    _check_required_files(errors)
    _check_tracked_files(tracked, errors)
    _check_markdown_links(tracked, errors)
    _check_component_status(errors)
    _check_ai_service_contract(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Repository validation passed ({len(tracked)} tracked files checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
