import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"


class CredentialReachedError(RuntimeError):
    pass


@pytest.fixture(params=["auth_init", "auth_update"])
def auth_hook(request, monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    hook = importlib.import_module(request.param)
    monkeypatch.setattr(hook, "load_azd_env", lambda: None)
    monkeypatch.setenv("AZURE_USE_AUTHENTICATION", "true")
    monkeypatch.delenv("AZURE_ENFORCE_ACCESS_CONTROL", raising=False)
    monkeypatch.delenv("AZURE_BYPASS_AUTHENTICATION_SETUP", raising=False)
    return hook


@pytest.mark.parametrize(
    ("override", "deployment_tenant", "expected"),
    [
        (None, "deployment-tenant", "deployment-tenant"),
        ("", "deployment-tenant", "deployment-tenant"),
        ("auth-tenant", "deployment-tenant", "auth-tenant"),
        ("auth-tenant", None, "auth-tenant"),
    ],
)
async def test_auth_hooks_resolve_tenant(
    auth_hook, monkeypatch, override, deployment_tenant, expected
) -> None:
    for name, value in (
        ("AZURE_AUTH_TENANT_ID", override),
        ("AZURE_TENANT_ID", deployment_tenant),
    ):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    credential = MagicMock(side_effect=CredentialReachedError)
    monkeypatch.setattr(auth_hook, "AzureDeveloperCliCredential", credential)

    with pytest.raises(CredentialReachedError):
        await auth_hook.main()

    credential.assert_called_once_with(tenant_id=expected)


@pytest.mark.parametrize("value", [None, ""])
async def test_auth_hooks_reject_missing_tenant(auth_hook, monkeypatch, capsys, value) -> None:
    for name in ("AZURE_AUTH_TENANT_ID", "AZURE_TENANT_ID"):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    credential = MagicMock()
    monkeypatch.setattr(auth_hook, "AzureDeveloperCliCredential", credential)

    with pytest.raises(SystemExit) as error:
        await auth_hook.main()

    assert error.value.code == 1
    assert "azd env set AZURE_AUTH_TENANT_ID tenant-id" in capsys.readouterr().out
    credential.assert_not_called()
