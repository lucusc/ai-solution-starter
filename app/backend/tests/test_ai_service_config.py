from scripts import validate_ai_service_config
from scripts.validate_ai_service_config import validate

COGNITIVE_ACCOUNT_PREFIX = (
    "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts"
)
ACCOUNT_ID = f"{COGNITIVE_ACCOUNT_PREFIX}/foundry"
PROJECT_ID = f"{ACCOUNT_ID}/projects/starter"
DOCUMENT_ID = f"{COGNITIVE_ACCOUNT_PREFIX}/docintel"


def test_default_configuration_disables_optional_services() -> None:
    assert validate({}) == []


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
            "FOUNDRY_CONNECT_BASE_OPENAI": "true",
            "OPENAI_HOST": "azure_custom",
        }
    )
    assert errors == ["FOUNDRY_CONNECT_BASE_OPENAI requires OPENAI_HOST=azure."]


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
