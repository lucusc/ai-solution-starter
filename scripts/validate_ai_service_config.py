#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections.abc import Mapping

ALLOWED_MODES = {"new", "existing", "none"}
ACCOUNT_ID = re.compile(
    r"^/subscriptions/[^/]+/resourceGroups/[^/]+/providers/"
    r"Microsoft\.CognitiveServices/accounts/(?P<account>[^/]+)$",
    re.IGNORECASE,
)
PROJECT_ID = re.compile(
    r"^(?P<account_id>/subscriptions/[^/]+/resourceGroups/[^/]+/providers/"
    r"Microsoft\.CognitiveServices/accounts/(?P<account>[^/]+))"
    r"/projects/(?P<project>[^/]+)$",
    re.IGNORECASE,
)
CONFIG_KEYS = (
    "USE_FOUNDRY",
    "USE_DOCUMENT_INTELLIGENCE",
    "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID",
    "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID",
    "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID",
    "FOUNDRY_CONNECT_BASE_OPENAI",
    "OPENAI_HOST",
    "AZURE_FOUNDRY_LOCATION",
    "AZURE_LOCATION",
)


def _value(values: Mapping[str, str], key: str, default: str = "") -> str:
    return values.get(key, default).strip()


def validate(values: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    foundry_mode = _value(values, "USE_FOUNDRY", "none") or "none"
    document_mode = _value(values, "USE_DOCUMENT_INTELLIGENCE", "none") or "none"
    foundry_account_id = _value(values, "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID")
    foundry_project_id = _value(values, "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID")
    document_id = _value(values, "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID")
    connect_openai = _value(values, "FOUNDRY_CONNECT_BASE_OPENAI", "false") or "false"
    openai_host = _value(values, "OPENAI_HOST", "azure") or "azure"

    for key, mode in (
        ("USE_FOUNDRY", foundry_mode),
        ("USE_DOCUMENT_INTELLIGENCE", document_mode),
    ):
        if mode not in ALLOWED_MODES:
            errors.append(f"{key} must be one of: existing, new, none.")

    if connect_openai not in {"true", "false"}:
        errors.append("FOUNDRY_CONNECT_BASE_OPENAI must be true or false.")
    if connect_openai == "true" and openai_host != "azure":
        errors.append("FOUNDRY_CONNECT_BASE_OPENAI requires OPENAI_HOST=azure.")

    account_match = ACCOUNT_ID.fullmatch(foundry_account_id) if foundry_account_id else None
    project_match = PROJECT_ID.fullmatch(foundry_project_id) if foundry_project_id else None
    document_match = ACCOUNT_ID.fullmatch(document_id) if document_id else None

    if foundry_account_id and account_match is None:
        errors.append(
            "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID must identify a "
            "Microsoft.CognitiveServices/accounts resource."
        )
    if foundry_project_id and project_match is None:
        errors.append(
            "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID must identify a "
            "Microsoft.CognitiveServices/accounts/projects resource."
        )
    if document_id and document_match is None:
        errors.append(
            "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID must identify a "
            "Microsoft.CognitiveServices/accounts resource."
        )

    if foundry_mode == "none":
        if foundry_account_id or foundry_project_id:
            errors.append("Foundry existing-resource IDs must be empty when USE_FOUNDRY=none.")
        if connect_openai == "true":
            errors.append("FOUNDRY_CONNECT_BASE_OPENAI requires USE_FOUNDRY=new or existing.")
    elif foundry_mode == "new":
        if foundry_account_id or foundry_project_id:
            errors.append("Foundry existing-resource IDs are not allowed when USE_FOUNDRY=new.")
    elif foundry_mode == "existing":
        if not foundry_account_id and not foundry_project_id:
            errors.append(
                "USE_FOUNDRY=existing requires EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID "
                "or EXISTING_FOUNDRY_PROJECT_RESOURCE_ID."
            )
        if account_match and project_match:
            project_account_id = project_match.group("account_id")
            if project_account_id.casefold() != foundry_account_id.casefold():
                errors.append("The Foundry project ID must belong to the configured account ID.")

    if document_mode == "none" and document_id:
        errors.append(
            "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID must be empty when "
            "USE_DOCUMENT_INTELLIGENCE=none."
        )
    elif document_mode == "new" and document_id:
        errors.append(
            "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID is not allowed when "
            "USE_DOCUMENT_INTELLIGENCE=new."
        )
    elif document_mode == "existing" and not document_id:
        errors.append(
            "USE_DOCUMENT_INTELLIGENCE=existing requires "
            "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID."
        )

    return errors


def _azd_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for key in CONFIG_KEYS:
        result = subprocess.run(
            ["azd", "env", "get-value", key],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            values[key] = result.stdout.strip()
    return values


def _azure_resource(resource_id: str) -> dict[str, str]:
    result = subprocess.run(
        [
            "az",
            "resource",
            "show",
            "--ids",
            resource_id,
            "--query",
            "{kind:kind,location:location}",
            "--output",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "resource lookup failed"
        raise RuntimeError(f"{resource_id}: {detail}")
    return json.loads(result.stdout)


def validate_azure_resources(values: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    foundry_mode = _value(values, "USE_FOUNDRY", "none") or "none"
    document_mode = _value(values, "USE_DOCUMENT_INTELLIGENCE", "none") or "none"
    foundry_account_id = _value(values, "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID")
    foundry_project_id = _value(values, "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID")
    document_id = _value(values, "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID")
    foundry_location = _value(values, "AZURE_FOUNDRY_LOCATION") or _value(values, "AZURE_LOCATION")

    if foundry_mode == "existing":
        account_id = foundry_account_id
        if not account_id and foundry_project_id:
            match = PROJECT_ID.fullmatch(foundry_project_id)
            account_id = match.group("account_id") if match else ""
        if account_id:
            try:
                account = _azure_resource(account_id)
                kind = account.get("kind", "")
                if kind.casefold() != "aiservices":
                    errors.append(
                        f"Existing Foundry account kind must be AIServices, found {kind}."
                    )
                if (
                    not foundry_project_id
                    and foundry_location
                    and account.get("location", "").casefold() != foundry_location.casefold()
                ):
                    errors.append(
                        "AZURE_FOUNDRY_LOCATION must match the existing Foundry account "
                        f"location {account.get('location', '')} when creating a project."
                    )
            except RuntimeError as exc:
                errors.append(f"Unable to validate existing Foundry account: {exc}")
        if foundry_project_id:
            try:
                _azure_resource(foundry_project_id)
            except RuntimeError as exc:
                errors.append(f"Unable to validate existing Foundry project: {exc}")

    if document_mode == "existing" and document_id:
        try:
            kind = _azure_resource(document_id).get("kind", "")
            if kind.casefold() != "formrecognizer":
                errors.append(
                    f"Existing Document Intelligence account kind must be FormRecognizer, "
                    f"found {kind}."
                )
        except RuntimeError as exc:
            errors.append(f"Unable to validate existing Document Intelligence account: {exc}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate optional AI service configuration.")
    parser.add_argument(
        "--from-azd",
        action="store_true",
        help="Read configuration from the selected Azure Developer CLI environment.",
    )
    parser.add_argument(
        "--check-azure",
        action="store_true",
        help="Verify selected existing resource kinds through read-only Azure CLI calls.",
    )
    args = parser.parse_args()

    values = _azd_values() if args.from_azd else dict(os.environ)
    errors = validate(values)
    if not errors and args.check_azure:
        errors.extend(validate_azure_resources(values))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Optional AI service configuration is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
