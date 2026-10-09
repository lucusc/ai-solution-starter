from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass
from typing import Any

from quart import Request

from .config import Settings
from .errors import AuthenticationError

CLIENT_PRINCIPAL_HEADER = "X-MS-CLIENT-PRINCIPAL"
MAX_PRINCIPAL_HEADER_BYTES = 16 * 1024
SUBJECT_CLAIMS = (
    "http://schemas.microsoft.com/identity/claims/objectidentifier",
    "oid",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
    "sub",
)


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    subject: str


def _claim_values(payload: dict[str, Any]) -> dict[str, str]:
    values: dict[str, str] = {}
    claims = payload.get("claims")
    if not isinstance(claims, list):
        return values
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        claim_type = claim.get("typ")
        claim_value = claim.get("val")
        if isinstance(claim_type, str) and isinstance(claim_value, str):
            values[claim_type] = claim_value
    return values


def _parse_client_principal(encoded: str) -> AuthenticatedUser:
    if len(encoded) > MAX_PRINCIPAL_HEADER_BYTES:
        raise AuthenticationError("The authenticated identity is invalid.")
    try:
        decoded = base64.b64decode(encoded, validate=True)
        payload = json.loads(decoded)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthenticationError("The authenticated identity is invalid.") from exc
    if not isinstance(payload, dict):
        raise AuthenticationError("The authenticated identity is invalid.")

    claims = _claim_values(payload)
    direct_user_id = payload.get("user_id")
    subject = direct_user_id if isinstance(direct_user_id, str) else None
    if not subject:
        subject = next((claims[name] for name in SUBJECT_CLAIMS if claims.get(name)), None)
    if not subject or len(subject) > 256:
        raise AuthenticationError("The authenticated identity is invalid.")
    return AuthenticatedUser(subject=subject)


def authenticate_request(request: Request, settings: Settings) -> AuthenticatedUser:
    if settings.local_auth_subject:
        return AuthenticatedUser(subject=settings.local_auth_subject)
    principal = request.headers.get(CLIENT_PRINCIPAL_HEADER)
    if not principal:
        raise AuthenticationError()
    return _parse_client_principal(principal)
