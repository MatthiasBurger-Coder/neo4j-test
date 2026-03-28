"""HTTP request model for framework-light inbound adapters."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HttpRequest:
    """Represents the minimal HTTP request data needed by the router."""

    method: str
    path: str
