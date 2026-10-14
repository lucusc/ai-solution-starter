from pathlib import Path

import pytest
from backend.config import ConfigurationError, Settings


def test_production_rejects_local_identity() -> None:
    with pytest.raises(ConfigurationError):
        Settings(
            storage_account="storage",
            storage_container="inputs",
            cosmos_account="cosmos",
            cosmos_database="starter",
            cosmos_container="inputs",
            running_in_production=True,
            local_auth_subject="local-user",
        )


def test_resolved_endpoints_use_account_names(settings: Settings) -> None:
    assert settings.resolved_storage_endpoint == ("https://starterstorage.blob.core.windows.net")
    assert settings.resolved_cosmos_endpoint == ("https://startercosmos.documents.azure.com:443/")


def test_from_environment_loads_local_dotenv_for_development(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    names = (
        "RUNNING_IN_PRODUCTION",
        "LOCAL_AUTH_SUBJECT",
        "AZURE_STORAGE_ACCOUNT",
        "AZURE_STORAGE_CONTAINER",
        "AZURE_COSMOSDB_ACCOUNT",
        "AZURE_COSMOSDB_DATABASE",
        "AZURE_COSMOSDB_CONTAINER",
    )
    for name in names:
        monkeypatch.delenv(name, raising=False)

    working_directory = tmp_path
    (working_directory / ".env").write_text(
        "\n".join(
            [
                "LOCAL_AUTH_SUBJECT=local-developer",
                "AZURE_STORAGE_ACCOUNT=storagefromdotenv",
                "AZURE_STORAGE_CONTAINER=inputs",
                "AZURE_COSMOSDB_ACCOUNT=cosmosfromdotenv",
                "AZURE_COSMOSDB_DATABASE=starter",
                "AZURE_COSMOSDB_CONTAINER=inputs",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(working_directory)

    settings = Settings.from_environment()

    assert settings.local_auth_subject == "local-developer"
    assert settings.storage_account == "storagefromdotenv"
    assert settings.cosmos_account == "cosmosfromdotenv"


def test_from_environment_preserves_existing_values_over_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "storage-from-env")
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "inputs")
    monkeypatch.setenv("AZURE_COSMOSDB_ACCOUNT", "cosmos-from-env")
    monkeypatch.setenv("AZURE_COSMOSDB_DATABASE", "starter")
    monkeypatch.setenv("AZURE_COSMOSDB_CONTAINER", "inputs")

    working_directory = tmp_path
    (working_directory / ".env").write_text(
        "\n".join(
            [
                "AZURE_STORAGE_ACCOUNT=storage-from-dotenv",
                "AZURE_COSMOSDB_ACCOUNT=cosmos-from-dotenv",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(working_directory)

    settings = Settings.from_environment()

    assert settings.storage_account == "storage-from-env"
    assert settings.cosmos_account == "cosmos-from-env"


def test_from_environment_ignores_dotenv_when_running_in_production(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    for name in (
        "LOCAL_AUTH_SUBJECT",
        "AZURE_STORAGE_ACCOUNT",
        "AZURE_STORAGE_CONTAINER",
        "AZURE_COSMOSDB_ACCOUNT",
        "AZURE_COSMOSDB_DATABASE",
        "AZURE_COSMOSDB_CONTAINER",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("RUNNING_IN_PRODUCTION", "true")

    working_directory = tmp_path
    (working_directory / ".env").write_text(
        "\n".join(
            [
                "AZURE_STORAGE_ACCOUNT=storagefromdotenv",
                "AZURE_STORAGE_CONTAINER=inputs",
                "AZURE_COSMOSDB_ACCOUNT=cosmosfromdotenv",
                "AZURE_COSMOSDB_DATABASE=starter",
                "AZURE_COSMOSDB_CONTAINER=inputs",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(working_directory)

    with pytest.raises(ConfigurationError, match="AZURE_STORAGE_ACCOUNT is required."):
        Settings.from_environment()
