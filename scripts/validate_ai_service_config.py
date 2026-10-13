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
OPENAI_ACCOUNT_ID = ACCOUNT_ID
PROJECT_ID = re.compile(
    r"^(?P<account_id>/subscriptions/[^/]+/resourceGroups/[^/]+/providers/"
    r"Microsoft\.CognitiveServices/accounts/(?P<account>[^/]+))"
    r"/projects/(?P<project>[^/]+)$",
    re.IGNORECASE,
)
CONFIG_KEYS = (
    "USE_FOUNDRY",
    "USE_OPENAI",
    "USE_DOCUMENT_INTELLIGENCE",
    "EXISTING_OPENAI_RESOURCE_ID",
    "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID",
    "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID",
    "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID",
    "FOUNDRY_CONNECT_BASE_OPENAI",
    "OPENAI_HOST",
    "DEPLOY_AZURE_OPENAI",
    "DEPLOY_AZURE_OPEN_MODELS",
    "DEPLOY_OPENAI_MODELS_EXISTING",
    "DEPLOY_FOUNDRY_MODEL_EXISTING",
    "AZURE_FOUNDRY_MODEL_DEPLOYMENT",
    "AZURE_FOUNDRY_LOCATION",
    "AZURE_OPENAI_LOCATION",
    "AZURE_LOCATION",
)
AZURE_OPENAI_LOCATIONS = {
    "australiaeast",
    "canadaeast",
    "eastus",
    "eastus2",
    "francecentral",
    "japaneast",
    "northcentralus",
    "swedencentral",
    "switzerlandnorth",
    "uksouth",
}


def _value(values: Mapping[str, str], key: str, default: str = "") -> str:
    return values.get(key, default).strip()


def validate(values: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    foundry_mode = _value(values, "USE_FOUNDRY", "new") or "new"
    openai_mode = _value(values, "USE_OPENAI", "none") or "none"
    document_mode = _value(values, "USE_DOCUMENT_INTELLIGENCE", "none") or "none"
    openai_resource_id = _value(values, "EXISTING_OPENAI_RESOURCE_ID")
    foundry_account_id = _value(values, "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID")
    foundry_project_id = _value(values, "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID")
    document_id = _value(values, "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID")
    openai_location = _value(values, "AZURE_OPENAI_LOCATION").casefold()
    connect_openai = _value(values, "FOUNDRY_CONNECT_BASE_OPENAI", "false") or "false"
    openai_host = _value(values, "OPENAI_HOST")
    legacy_openai_create = _value(values, "DEPLOY_AZURE_OPENAI")
    legacy_openai_models = _value(values, "DEPLOY_AZURE_OPEN_MODELS")
    deploy_existing_openai_models = (
        _value(values, "DEPLOY_OPENAI_MODELS_EXISTING", "false") or "false"
    )
    deploy_existing_foundry_model = (
        _value(values, "DEPLOY_FOUNDRY_MODEL_EXISTING", "false") or "false"
    )

    for key, mode in (
        ("USE_FOUNDRY", foundry_mode),
        ("USE_OPENAI", openai_mode),
        ("USE_DOCUMENT_INTELLIGENCE", document_mode),
    ):
        if mode not in ALLOWED_MODES:
            errors.append(f"{key} must be one of: existing, new, none.")
    if connect_openai not in {"true", "false"}:
        errors.append("FOUNDRY_CONNECT_BASE_OPENAI must be true or false.")
    for key, value in (
        ("DEPLOY_AZURE_OPENAI", legacy_openai_create),
        ("DEPLOY_AZURE_OPEN_MODELS", legacy_openai_models),
        ("DEPLOY_OPENAI_MODELS_EXISTING", deploy_existing_openai_models),
        ("DEPLOY_FOUNDRY_MODEL_EXISTING", deploy_existing_foundry_model),
    ):
        if value and value not in {"true", "false"}:
            errors.append(f"{key} must be true or false.")

    if legacy_openai_create in {"true", "false"}:
        legacy_mode = (
            "new"
            if legacy_openai_create == "true"
            else ("existing" if openai_resource_id else "none")
        )
        if openai_mode != legacy_mode:
            errors.append(
                f"DEPLOY_AZURE_OPENAI={legacy_openai_create} conflicts with "
                f"USE_OPENAI={openai_mode}; remove the legacy setting or set "
                f"USE_OPENAI={legacy_mode}."
            )
    if legacy_openai_models == "true":
        if openai_mode == "none":
            errors.append("DEPLOY_AZURE_OPEN_MODELS=true requires USE_OPENAI=new or existing.")
        elif openai_mode == "existing" and deploy_existing_openai_models != "true":
            errors.append(
                "Set DEPLOY_OPENAI_MODELS_EXISTING=true to explicitly deploy models "
                "into an existing Azure OpenAI account."
            )
    elif legacy_openai_models == "false" and openai_mode == "new":
        errors.append(
            "DEPLOY_AZURE_OPEN_MODELS=false conflicts with USE_OPENAI=new, "
            "which creates the selected model deployments."
        )

    if openai_host == "azure" and not _value(values, "USE_OPENAI"):
        errors.append(
            "OPENAI_HOST=azure is a legacy provider selection; set USE_OPENAI explicitly "
            "to new, existing, or none."
        )
    if connect_openai == "true" and (openai_host and openai_host != "azure"):
        errors.append("FOUNDRY_CONNECT_BASE_OPENAI requires OPENAI_HOST=azure.")
    if connect_openai == "true" and openai_mode == "none":
        errors.append("FOUNDRY_CONNECT_BASE_OPENAI requires USE_OPENAI=new or existing.")

    openai_match = OPENAI_ACCOUNT_ID.fullmatch(openai_resource_id) if openai_resource_id else None
    account_match = ACCOUNT_ID.fullmatch(foundry_account_id) if foundry_account_id else None
    project_match = PROJECT_ID.fullmatch(foundry_project_id) if foundry_project_id else None
    document_match = ACCOUNT_ID.fullmatch(document_id) if document_id else None

    if openai_resource_id and openai_match is None:
        errors.append(
            "EXISTING_OPENAI_RESOURCE_ID must identify a "
            "Microsoft.CognitiveServices/accounts resource."
        )
    if openai_mode == "none" and openai_resource_id:
        errors.append("EXISTING_OPENAI_RESOURCE_ID must be empty when USE_OPENAI=none.")
    elif openai_mode == "new" and openai_resource_id:
        errors.append("EXISTING_OPENAI_RESOURCE_ID is not allowed when USE_OPENAI=new.")
    elif openai_mode == "existing" and not openai_resource_id:
        errors.append("USE_OPENAI=existing requires EXISTING_OPENAI_RESOURCE_ID.")
    if openai_mode == "new" and not openai_location:
        errors.append("AZURE_OPENAI_LOCATION is required when USE_OPENAI=new.")
    elif openai_mode == "new" and openai_location not in AZURE_OPENAI_LOCATIONS:
        errors.append(
            "AZURE_OPENAI_LOCATION must be a supported Azure OpenAI region: "
            + ", ".join(sorted(AZURE_OPENAI_LOCATIONS))
            + "."
        )

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
    foundry_mode = _value(values, "USE_FOUNDRY", "new") or "new"
    openai_mode = _value(values, "USE_OPENAI", "none") or "none"
    document_mode = _value(values, "USE_DOCUMENT_INTELLIGENCE", "none") or "none"
    foundry_account_id = _value(values, "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID")
    foundry_project_id = _value(values, "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID")
    document_id = _value(values, "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID")
    openai_resource_id = _value(values, "EXISTING_OPENAI_RESOURCE_ID")
    foundry_location = _value(values, "AZURE_FOUNDRY_LOCATION") or _value(values, "AZURE_LOCATION")

    if foundry_mode == "existing":
        account_id = foundry_account_id
        if not account_id and foundry_project_id:
            match = PROJECT_ID.fullmatch(foundry_project_id)
            account_id = match.group("account_id") if match else ""
        if account_id and _value(values, "DEPLOY_FOUNDRY_MODEL_EXISTING", "false") != "true":
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
        if account_id:
            deployment_name = (
                _value(values, "AZURE_FOUNDRY_MODEL_DEPLOYMENT", "starter-gpt-4o")
                or "starter-gpt-4o"
            )
            try:
                _azure_resource(f"{account_id}/deployments/{deployment_name}")
            except RuntimeError as exc:
                errors.append(
                    "The selected existing Foundry account must contain model deployment "
                    f"{deployment_name}: {exc}"
                )

    if openai_mode == "existing" and openai_resource_id:
        try:
            kind = _azure_resource(openai_resource_id).get("kind", "")
            if kind.casefold() not in {"openai", "aiservices"}:
                errors.append(
                    "Existing Azure OpenAI account kind must be OpenAI or AIServices, "
                    f"found {kind}."
                )
        except RuntimeError as exc:
            errors.append(f"Unable to validate existing Azure OpenAI account: {exc}")

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
