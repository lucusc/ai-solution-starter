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
