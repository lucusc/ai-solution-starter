from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int
    details: dict[str, Any] | None = None


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication is required.") -> None:
        super().__init__("authentication_required", message, 401)


class NotFoundError(AppError):
    def __init__(self, message: str = "The requested work item was not found.") -> None:
        super().__init__("work_item_not_found", message, 404)


class ConflictError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("work_item_conflict", message, 409)


class DependencyError(AppError):
    def __init__(self, code: str, message: str, *, unavailable: bool) -> None:
        super().__init__(code, message, 503 if unavailable else 502)


class RequestValidationError(AppError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        status_code: int = 400,
    ) -> None:
        super().__init__(code, message, status_code, details)
