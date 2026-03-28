"""JSON-only HTTP response model."""

from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any


@dataclass(frozen=True, slots=True)
class JsonResponse:
    """Represents a JSON-only HTTP response."""

    status_code: int
    payload: Any
    headers: tuple[tuple[str, str], ...] = field(
        default_factory=lambda: (("Content-Type", "application/json; charset=utf-8"),)
    )

    @property
    def status_line(self) -> str:
        """Return the WSGI-compatible status line."""
        return f"{self.status_code} {HTTPStatus(self.status_code).phrase}"


def json_ok(payload: Any) -> JsonResponse:
    """Create a successful JSON response."""
    return JsonResponse(status_code=HTTPStatus.OK, payload=payload)


def json_created(payload: Any) -> JsonResponse:
    """Create a created JSON response."""
    return JsonResponse(status_code=HTTPStatus.CREATED, payload=payload)


def json_error(*, status_code: int, code: str, message: str) -> JsonResponse:
    """Create a JSON response for structured API errors."""
    return JsonResponse(
        status_code=status_code,
        payload={"error": {"code": code, "message": message}},
    )


def json_bad_request(*, code: str, message: str) -> JsonResponse:
    """Create a JSON response for invalid client input."""
    return json_error(status_code=HTTPStatus.BAD_REQUEST, code=code, message=message)


def json_not_found(*, code: str, message: str) -> JsonResponse:
    """Create a JSON response for missing resources."""
    return json_error(status_code=HTTPStatus.NOT_FOUND, code=code, message=message)


def json_unsupported_media_type(*, code: str, message: str) -> JsonResponse:
    """Create a JSON response for unsupported request media types."""
    return json_error(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, code=code, message=message)


def json_unprocessable_entity(*, code: str, message: str) -> JsonResponse:
    """Create a JSON response for semantically invalid client input."""
    return json_error(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, code=code, message=message)


def json_internal_server_error() -> JsonResponse:
    """Create a JSON response for unexpected server failures."""
    return json_error(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        code="internal_error",
        message="Internal server error",
    )
