import base64
import json

import pytest
from backend.auth import authenticate_request
from backend.config import Settings
from backend.errors import AuthenticationError
from quart import Quart


def _settings() -> Settings:
    return Settings(
        storage_account="storage",
        storage_container="inputs",
        cosmos_account="cosmos",
        cosmos_database="starter",
        cosmos_container="inputs",
    )


@pytest.mark.asyncio
async def test_easy_auth_subject_is_extracted() -> None:
    app = Quart(__name__)
    payload = {
        "claims": [
            {
                "typ": "http://schemas.microsoft.com/identity/claims/objectidentifier",
                "val": "owner-123",
            }
        ]
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    async with app.test_request_context(
        "/api/v1/work-items",
        headers={"X-MS-CLIENT-PRINCIPAL": encoded},
    ):
        from quart import request

        user = authenticate_request(request, _settings())
    assert user.subject == "owner-123"


@pytest.mark.asyncio
async def test_missing_easy_auth_identity_is_rejected() -> None:
    app = Quart(__name__)
    async with app.test_request_context("/api/v1/work-items"):
        from quart import request

        with pytest.raises(AuthenticationError):
            authenticate_request(request, _settings())
