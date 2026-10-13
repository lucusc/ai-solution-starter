#!/usr/bin/env python3
"""Validate the Logic Apps Standard package and its Foundry-only contract."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "app" / "agent" / "workflows"
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
REQUIRED_APP_SETTINGS = {
    "AZURE_STORAGE_INPUT_CONTAINER",
    "AZURE_STORAGE_INSTRUCTIONS_CONTAINER",
    "AZURE_STORAGE_ACCOUNT",
    "AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE",
    "AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE",
    "AZURE_COSMOS_ACCOUNT_URI",
    "AZURE_COSMOS_DATABASE",
    "AZURE_COSMOS_CONTAINER",
    "AZURE_FOUNDRY_INFERENCE_ENDPOINT",
    "AZURE_FOUNDRY_DEPLOYMENT_NAME",
    "WORKFLOWS_IDENTITY_RESOURCE_ID",
}
FORBIDDEN_CONFIG_KEYS = {
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_KEY",
}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object.")
    return value


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _find_action(actions: Any, name: str) -> dict[str, Any] | None:
    if isinstance(actions, dict):
        for action_name, action in actions.items():
            if action_name == name and isinstance(action, dict):
                return action
            found = _find_action(action, name)
            if found is not None:
                return found
    elif isinstance(actions, list):
        for action in actions:
            found = _find_action(action, name)
            if found is not None:
                return found
    return None


def validate_package() -> list[str]:
    errors: list[str] = []
    required_files = (
        PACKAGE / "host.json",
        PACKAGE / "connections.json",
        PACKAGE / "parameters.json",
        PACKAGE / "azure.parameters.json",
        PACKAGE / "process-document" / "workflow.json",
    )
    for path in required_files:
        if not path.is_file():
            errors.append(f"Required package file is missing: {path.relative_to(ROOT)}")
    if errors:
        return errors

    connections = _load_json(PACKAGE / "connections.json")
    local_parameters = _load_json(PACKAGE / "parameters.json")
    azure_parameters = _load_json(PACKAGE / "azure.parameters.json")
    workflow = _load_json(PACKAGE / "process-document" / "workflow.json")
    workflow_definition = workflow.get("definition", {})

    connection = connections.get("serviceProviderConnections", {}).get("azureblob", {})
    if connection.get("serviceProvider", {}).get("id") != "/serviceProviders/AzureBlob":
        errors.append("The package must use the Standard built-in Azure Blob service provider.")
    if connection.get("parameterSetName") != "ManagedServiceIdentity":
        errors.append("The Blob connection must use managed identity.")
    if (
        connection.get("parameterValues", {}).get("storageAccountName")
        != "@appsetting('AZURE_STORAGE_ACCOUNT')"
    ):
        errors.append("The Blob connection must use the provisioned storage account app setting.")

    parameter_names = set(workflow_definition.get("parameters", {}))
    if parameter_names != set(local_parameters) or parameter_names != set(azure_parameters):
        errors.append("Workflow, local, and Azure parameter names must match exactly.")
    for parameter, config in azure_parameters.items():
        value = config.get("value", "")
        referenced = set(re.findall(r"@appsetting\('([^']+)'\)", value))
        if not value.startswith("@appsetting(") or len(referenced) != 1:
            errors.append(f"Azure parameter {parameter} must use one app-setting reference.")
        missing = referenced - REQUIRED_APP_SETTINGS
        if missing:
            errors.append(
                f"Azure parameter {parameter} references unsupported settings: {missing}."
            )
    for parameter, config in local_parameters.items():
        if not config.get("value"):
            errors.append(f"Local parameter {parameter} must have a synthetic value.")
        if (
            parameter == "workflowsIdentityResourceId"
            and "00000000-0000-0000-0000-000000000000" not in config["value"]
        ):
            errors.append("The local managed-identity parameter must be a synthetic placeholder.")
    for key in FORBIDDEN_CONFIG_KEYS:
        if key in json.dumps(connections) or key in json.dumps(azure_parameters):
            errors.append(f"Standalone OpenAI setting {key} must not be required by this package.")

    triggers = workflow_definition.get("triggers", {})
    trigger = triggers.get("Blob_added_or_updated", {})
    if trigger.get("type") != "ServiceProvider":
        errors.append("The workflow must use a built-in Blob service-provider trigger.")
    trigger_config = trigger.get("inputs", {}).get("serviceProviderConfiguration", {})
    if trigger_config.get("operationId") != "onUpdatedFile":
        errors.append("The Blob trigger must use the onUpdatedFile operation.")
    if trigger.get("runtimeConfiguration", {}).get("concurrency", {}).get("runs") != 1:
        errors.append("Blob trigger concurrency must be limited to one run.")

    actions = list(_walk(workflow_definition.get("actions", {})))
    action_types = {action.get("type") for action in actions}
    if "Http" not in action_types or "ParseJson" not in action_types:
        errors.append("The workflow must call the Foundry API and parse its structured result.")
    workflow_text = json.dumps(workflow_definition)
    required_actions = {
        "Claim_processing_with_etag",
        "Mark_claimed",
        "Read_source_pdf",
        "Read_system_instructions",
        "Read_processing_instructions",
        "Invoke_foundry_responses",
        "Require_complete_foundry_response",
        "Validate_foundry_response",
        "Persist_completed_with_etag",
        "Handle_claimed_failure",
    }
    for action_name in required_actions:
        if _find_action(workflow_definition.get("actions", {}), action_name) is None:
            errors.append(f"Workflow action is missing: {action_name}.")
    claim = _find_action(workflow_definition.get("actions", {}), "Claim_processing_with_etag")
    mark_claimed = _find_action(workflow_definition.get("actions", {}), "Mark_claimed")
    read_source = _find_action(workflow_definition.get("actions", {}), "Read_source_pdf")
    invoke_foundry = _find_action(
        workflow_definition.get("actions", {}), "Invoke_foundry_responses"
    )
    persist = _find_action(workflow_definition.get("actions", {}), "Persist_completed_with_etag")
    require_complete = _find_action(
        workflow_definition.get("actions", {}), "Require_complete_foundry_response"
    )
    validate_result = _find_action(
        workflow_definition.get("actions", {}), "Validate_foundry_response"
    )
    if claim and "If-Match" not in claim.get("inputs", {}).get("headers", {}):
        errors.append("The processing claim must use the current Cosmos ETag.")
    if mark_claimed and mark_claimed.get("runAfter", {}).get("Claim_processing_with_etag") != [
        "Succeeded"
    ]:
        errors.append("The claimed flag must only be set after the ETag claim succeeds.")
    if read_source and read_source.get("runAfter", {}).get("Mark_claimed") != ["Succeeded"]:
        errors.append("The source PDF must not be read before a successful claim.")
    if invoke_foundry and invoke_foundry.get("runAfter", {}).get(
        "Read_processing_instructions"
    ) != ["Succeeded"]:
        errors.append("Foundry inference must follow the successful claim and asset reads.")
    if persist and persist.get("runAfter", {}).get("Require_complete_foundry_response") != [
        "Succeeded"
    ]:
        errors.append("Only validated Foundry output may be persisted as completed.")
    if persist and "If-Match" not in persist.get("inputs", {}).get("headers", {}):
        errors.append("Completion persistence must use the claimed Cosmos ETag.")
    if (
        validate_result
        and validate_result.get("inputs", {}).get("schema", {}).get("additionalProperties")
        is not False
    ):
        errors.append("Foundry output validation must reject unknown result fields.")
    if require_complete and require_complete.get("expression", {}).get("equals", [None])[1] != (
        "completed"
    ):
        errors.append("Incomplete or refused Foundry responses must be rejected.")
    for action_name in (
        "Query_work_item",
        "Refresh_work_item",
        "Read_source_pdf",
        "Read_system_instructions",
        "Read_processing_instructions",
        "Invoke_foundry_responses",
        "Persist_completed_with_etag",
        "Replace_processing_with_safe_failure",
    ):
        action = _find_action(workflow_definition.get("actions", {}), action_name)
        if action and "retryPolicy" not in action:
            errors.append(f"Dependency action {action_name} must have a bounded retry policy.")
        if action and isinstance(action.get("inputs"), dict) and "retryPolicy" in action["inputs"]:
            errors.append(f"Retry policy for {action_name} must be at action level.")
    for required in (
        "work-items/",
        "/source.pdf",
        "20971520",
        "x-ms-documentdb-partitionkey",
        "If-Match",
        "formatDateTime(utcNow(), 'R')",
        "queued",
        "processing",
        "completed",
        "ai_processing_failed",
        "queue_transition_timeout",
        "processing_claim_conflict",
        "foundryInferenceEndpoint",
        "foundryDeploymentName",
        "https://ai.azure.com",
        "json_schema",
        "action_required",
        "key_points",
        "store",
        "secureData",
        "currentRecord",
        "Readiness_timeout",
        "Persist_safe_failed_state",
    ):
        if required not in workflow_text:
            errors.append(f"Workflow is missing required contract marker: {required}.")
    if "openai.azure.com/openai" in workflow_text or "AZURE_OPENAI_ENDPOINT" in workflow_text:
        errors.append("Inference must use the configured Foundry endpoint, not standalone OpenAI.")
    for action in actions:
        secure_data = action.get("runtimeConfiguration", {}).get("secureData")
        if action.get("type") in {"Http", "ServiceProvider"} and not secure_data:
            errors.append(
                "Every content-bearing HTTP and Blob action must secure run-history data."
            )
            break
    nested_actions = list(_walk(workflow_definition.get("actions", {})))
    initialized_variables = [
        action for action in nested_actions if action.get("type") == "InitializeVariable"
    ]
    root_actions = workflow_definition.get("actions", {})
    if len(initialized_variables) != 1 or "Initialize_workflow_state" not in root_actions:
        errors.append("Workflow variables must be initialized once at the top action level.")
    if workflow_text.count("formatDateTime(utcNow(), 'R')") < 4:
        errors.append("Cosmos REST calls must use RFC 1123 dates.")

    for fixture in (
        ROOT / "app" / "agent" / "tests" / "fixtures" / "blob-trigger.json",
        ROOT / "app" / "agent" / "tests" / "fixtures" / "queued-work-item.json",
        ROOT / "app" / "agent" / "tests" / "fixtures" / "foundry-success.json",
        ROOT / "app" / "agent" / "tests" / "fixtures" / "foundry-invalid-output.json",
    ):
        _load_json(fixture)
    pdf_fixture = ROOT / "app" / "agent" / "tests" / "fixtures" / "synthetic.pdf"
    if not pdf_fixture.is_file() or not pdf_fixture.read_bytes().startswith(b"%PDF-"):
        errors.append("The synthetic PDF workflow fixture is missing or invalid.")

    return errors


def is_canonical_work_item_path(path: str) -> bool:
    parts = path.split("/")
    return (
        len(parts) == 3
        and parts[0] == "work-items"
        and parts[2] == "source.pdf"
        and UUID_PATTERN.fullmatch(parts[1]) is not None
    )


def main() -> int:
    errors = validate_package()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Logic Apps package structure and Foundry workflow contract are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
