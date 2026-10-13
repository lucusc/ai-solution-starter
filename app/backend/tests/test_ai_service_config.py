from itertools import product

from scripts import validate_ai_service_config
from scripts.validate_ai_service_config import ALLOWED_MODES, validate

COGNITIVE_ACCOUNT_PREFIX = (
    "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts"
)
ACCOUNT_ID = f"{COGNITIVE_ACCOUNT_PREFIX}/foundry"
PROJECT_ID = f"{ACCOUNT_ID}/projects/starter"
DOCUMENT_ID = f"{COGNITIVE_ACCOUNT_PREFIX}/docintel"
OPENAI_ID = f"{COGNITIVE_ACCOUNT_PREFIX}/openai"


def test_default_configuration_uses_foundry_and_disables_other_optional_services() -> None:
    assert validate({}) == []


def test_all_service_mode_combinations_validate() -> None:
    for foundry_mode, openai_mode, document_mode in product(ALLOWED_MODES, repeat=3):
        values = {
            "USE_FOUNDRY": foundry_mode,
            "USE_OPENAI": openai_mode,
            "USE_DOCUMENT_INTELLIGENCE": document_mode,
        }
        if openai_mode == "new":
            values["AZURE_OPENAI_LOCATION"] = "eastus2"
        if foundry_mode == "existing":
            values["EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID"] = ACCOUNT_ID
        if openai_mode == "existing":
            values["EXISTING_OPENAI_RESOURCE_ID"] = OPENAI_ID
        if document_mode == "existing":
            values["EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID"] = DOCUMENT_ID
        assert validate(values) == [], (foundry_mode, openai_mode, document_mode)


def test_openai_modes_require_or_reject_existing_resource_id() -> None:
    assert validate({"USE_OPENAI": "existing"}) == [
        "USE_OPENAI=existing requires EXISTING_OPENAI_RESOURCE_ID."
    ]
    assert validate(
        {
            "USE_OPENAI": "new",
            "AZURE_OPENAI_LOCATION": "eastus2",
            "EXISTING_OPENAI_RESOURCE_ID": OPENAI_ID,
        }
    ) == ["EXISTING_OPENAI_RESOURCE_ID is not allowed when USE_OPENAI=new."]
    assert validate({"USE_OPENAI": "none", "EXISTING_OPENAI_RESOURCE_ID": OPENAI_ID}) == [
        "EXISTING_OPENAI_RESOURCE_ID must be empty when USE_OPENAI=none."
    ]


def test_openai_existing_resource_id_must_be_an_account_id() -> None:
    assert validate(
        {
            "USE_OPENAI": "existing",
            "EXISTING_OPENAI_RESOURCE_ID": "/subscriptions/sub/resourceGroups/rg",
        }
    ) == [
        "EXISTING_OPENAI_RESOURCE_ID must identify a Microsoft.CognitiveServices/accounts resource."
    ]


def test_openai_new_mode_requires_supported_resource_region() -> None:
    assert validate({"USE_OPENAI": "new"}) == [
        "AZURE_OPENAI_LOCATION is required when USE_OPENAI=new."
    ]
    errors = validate({"USE_OPENAI": "new", "AZURE_OPENAI_LOCATION": "antarctica"})
    assert errors and errors[0].startswith("AZURE_OPENAI_LOCATION must be a supported")


def test_new_modes_reject_existing_resource_ids() -> None:
    errors = validate(
        {
            "USE_FOUNDRY": "new",
            "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID": ACCOUNT_ID,
            "USE_DOCUMENT_INTELLIGENCE": "new",
            "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID": DOCUMENT_ID,
        }
    )
    assert len(errors) == 2


def test_existing_modes_accept_well_formed_resource_ids() -> None:
    assert (
        validate(
            {
                "USE_FOUNDRY": "existing",
                "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID": PROJECT_ID,
                "USE_DOCUMENT_INTELLIGENCE": "existing",
                "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID": DOCUMENT_ID,
            }
        )
        == []
    )


def test_existing_modes_require_resource_ids() -> None:
    errors = validate(
        {
            "USE_FOUNDRY": "existing",
            "USE_DOCUMENT_INTELLIGENCE": "existing",
        }
    )
    assert len(errors) == 2


def test_project_must_belong_to_selected_foundry_account() -> None:
    errors = validate(
        {
            "USE_FOUNDRY": "existing",
            "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID": ACCOUNT_ID,
            "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID": (
                "/subscriptions/sub/resourceGroups/rg/providers/"
                "Microsoft.CognitiveServices/accounts/other/projects/starter"
            ),
        }
    )
    assert errors == ["The Foundry project ID must belong to the configured account ID."]


def test_none_modes_reject_stale_ids_and_connection_request() -> None:
    errors = validate(
        {
            "EXISTING_FOUNDRY_PROJECT_RESOURCE_ID": PROJECT_ID,
            "FOUNDRY_CONNECT_BASE_OPENAI": "true",
            "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID": DOCUMENT_ID,
        }
    )
    assert len(errors) == 3


def test_foundry_connection_requires_baseline_azure_openai() -> None:
    errors = validate(
        {
            "USE_FOUNDRY": "new",
            "USE_OPENAI": "new",
            "AZURE_OPENAI_LOCATION": "eastus2",
            "FOUNDRY_CONNECT_BASE_OPENAI": "true",
            "OPENAI_HOST": "azure_custom",
        }
    )
    assert errors == ["FOUNDRY_CONNECT_BASE_OPENAI requires OPENAI_HOST=azure."]


def test_foundry_connection_requires_enabled_openai_mode() -> None:
    assert validate(
        {
            "USE_FOUNDRY": "new",
            "USE_OPENAI": "none",
            "FOUNDRY_CONNECT_BASE_OPENAI": "true",
        }
    ) == ["FOUNDRY_CONNECT_BASE_OPENAI requires USE_OPENAI=new or existing."]


def test_legacy_openai_create_setting_requires_matching_new_mode() -> None:
    errors = validate({"DEPLOY_AZURE_OPENAI": "true"})
    assert any("conflicts with USE_OPENAI=none" in error for error in errors)
    assert (
        validate(
            {
                "USE_OPENAI": "new",
                "AZURE_OPENAI_LOCATION": "eastus2",
                "DEPLOY_AZURE_OPENAI": "true",
            }
        )
        == []
    )


def test_legacy_explicit_azure_host_requires_new_selector() -> None:
    assert validate({"OPENAI_HOST": "azure"}) == [
        "OPENAI_HOST=azure is a legacy provider selection; set USE_OPENAI explicitly "
        "to new, existing, or none."
    ]


def test_existing_foundry_model_deployment_is_an_explicit_input() -> None:
    assert validate(
        {
            "USE_FOUNDRY": "existing",
            "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID": ACCOUNT_ID,
            "DEPLOY_FOUNDRY_MODEL_EXISTING": "not-a-boolean",
        }
    ) == ["DEPLOY_FOUNDRY_MODEL_EXISTING must be true or false."]


def test_modes_and_resource_shapes_are_case_sensitive_and_exact() -> None:
    errors = validate(
        {
            "USE_FOUNDRY": "New",
            "USE_DOCUMENT_INTELLIGENCE": "existing",
            "EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID": (
                "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Search/searchServices/search"
            ),
        }
    )
    assert len(errors) == 2


def test_existing_foundry_project_location_must_match_account(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        validate_ai_service_config,
        "_azure_resource",
        lambda _: {"kind": "AIServices", "location": "eastus"},
    )
    errors = validate_ai_service_config.validate_azure_resources(
        {
            "USE_FOUNDRY": "existing",
            "EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID": ACCOUNT_ID,
            "AZURE_FOUNDRY_LOCATION": "westus",
        }
    )
    assert errors == [
        "AZURE_FOUNDRY_LOCATION must match the existing Foundry account "
        "location eastus when creating a project."
    ]
