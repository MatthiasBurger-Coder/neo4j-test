"""HTTP request model for framework-light inbound adapters."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class HttpRequest:
    """Represents the minimal HTTP request data needed by the router."""

    method: str
    path: str
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes = b""

    def __post_init__(self) -> None:
        """Normalize headers for case-insensitive lookups."""
        object.__setattr__(
            self,
            "headers",
            {str(name).lower(): str(value) for name, value in self.headers.items()},
        )

    def header(self, name: str) -> str | None:
        """Return a normalized header value when present."""
        return self.headers.get(name.lower())
