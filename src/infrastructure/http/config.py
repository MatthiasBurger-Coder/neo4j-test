"""Configuration for the lightweight HTTP server."""

import os
from dataclasses import dataclass

from src.infrastructure.validation import require_non_blank, require_positive_integer


@dataclass(frozen=True, slots=True)
class HttpServerConfig:
    """Validated configuration for the local WSGI server."""

    host: str = "127.0.0.1"
    port: int = 8080

    def __post_init__(self) -> None:
        """Validate server host and port settings."""
        object.__setattr__(
            self,
            "host",
            require_non_blank(owner=self.__class__.__name__, field_name="host", value=self.host),
        )
        require_positive_integer(owner=self.__class__.__name__, field_name="port", value=self.port)

    @staticmethod
    def from_env() -> "HttpServerConfig":
        """Load the HTTP server configuration from the environment."""
        return HttpServerConfig(
            host=os.getenv("APP_HOST", "127.0.0.1"),
            port=int(os.getenv("APP_PORT", "8080")),
        )
