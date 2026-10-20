from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when backend configuration is invalid."""


TRUE_VALUES = {"1", "true", "yes", "on"}


def _bool_value(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be a boolean value.")


def _int_value(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer.") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(f"{name} must be between {minimum} and {maximum}.")
    return value


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(f"{name} is required.")
    return value


def _dotenv_candidates() -> tuple[Path, ...]:
    backend_root = Path(__file__).resolve().parents[1]
    candidates = [
        Path.cwd() / ".env",
        backend_root / ".env",
    ]
    if len(backend_root.parents) > 1:
        candidates.append(backend_root.parents[1] / ".env")
    deduplicated: list[Path] = []
    seen_paths: set[Path] = set()
    for candidate in candidates:
        normalized = candidate.resolve()
        if normalized in seen_paths:
            continue
        seen_paths.add(normalized)
        deduplicated.append(candidate)
    return tuple(deduplicated)


def _load_local_dotenv() -> None:
    if _bool_value("RUNNING_IN_PRODUCTION"):
        return
    for candidate in _dotenv_candidates():
        if not candidate.is_file():
            continue
        try:
            from dotenv import load_dotenv
        except ImportError as exc:
            raise ConfigurationError(
                "python-dotenv is required to load a local .env file. "
                "Install app/backend/requirements-dev.txt or remove the .env file."
            ) from exc
        load_dotenv(dotenv_path=candidate, override=False)
        return


@dataclass(frozen=True, slots=True)
class Settings:
    storage_account: str
    storage_container: str
    cosmos_account: str
    cosmos_database: str
    cosmos_container: str
    storage_endpoint: str | None = None
    cosmos_endpoint: str | None = None
    application_insights_connection_string: str | None = None
    running_in_production: bool = False
    local_auth_subject: str | None = None
    max_pdf_size_mb: int = 20
    default_page_size: int = 20
    max_page_size: int = 100
    readiness_cache_seconds: int = 30
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        if self.running_in_production and self.local_auth_subject:
            raise ConfigurationError(
                "LOCAL_AUTH_SUBJECT cannot be configured when RUNNING_IN_PRODUCTION is true."
            )
        if not 1 <= self.default_page_size <= self.max_page_size:
            raise ConfigurationError("DEFAULT_PAGE_SIZE must be between 1 and MAX_PAGE_SIZE.")

    @property
    def max_pdf_size_bytes(self) -> int:
        return self.max_pdf_size_mb * 1024 * 1024

    @property
    def resolved_storage_endpoint(self) -> str:
        return self.storage_endpoint or (f"https://{self.storage_account}.blob.core.windows.net")

    @property
    def resolved_cosmos_endpoint(self) -> str:
        return self.cosmos_endpoint or (f"https://{self.cosmos_account}.documents.azure.com:443/")

    @classmethod
    def from_environment(cls) -> Settings:
        _load_local_dotenv()
        local_subject = os.getenv("LOCAL_AUTH_SUBJECT", "").strip() or None
        return cls(
            storage_account=_required("AZURE_STORAGE_ACCOUNT"),
            storage_container=_required("AZURE_STORAGE_CONTAINER"),
            cosmos_account=_required("AZURE_COSMOSDB_ACCOUNT"),
            cosmos_database=_required("AZURE_COSMOSDB_DATABASE"),
            cosmos_container=_required("AZURE_COSMOSDB_CONTAINER"),
            storage_endpoint=os.getenv("AZURE_STORAGE_ENDPOINT") or None,
            cosmos_endpoint=os.getenv("AZURE_COSMOSDB_ENDPOINT") or None,
            application_insights_connection_string=(
                os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING") or None
            ),
            running_in_production=_bool_value("RUNNING_IN_PRODUCTION"),
            local_auth_subject=local_subject,
            max_pdf_size_mb=_int_value("MAX_PDF_SIZE_MB", 20, 1, 100),
            default_page_size=_int_value("DEFAULT_PAGE_SIZE", 20, 1, 100),
            max_page_size=_int_value("MAX_PAGE_SIZE", 100, 1, 1000),
            readiness_cache_seconds=_int_value("READINESS_CACHE_SECONDS", 30, 1, 300),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
