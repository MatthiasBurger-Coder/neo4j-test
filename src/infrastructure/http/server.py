"""WSGI HTTP server for the JSON-only address API."""

import logging
from wsgiref.simple_server import make_server

from src.adapters.inbound.http.wsgi_application import JsonWsgiApplication
from src.infrastructure.http.config import HttpServerConfig


class WsgiHttpServer:
    """Runs the JSON WSGI application on a local HTTP socket."""

    def __init__(
        self,
        *,
        config: HttpServerConfig,
        wsgi_application: JsonWsgiApplication,
        logger: logging.Logger | None = None,
    ) -> None:
        self._config = config
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._server = make_server(config.host, config.port, wsgi_application)

    def serve_forever(self) -> None:
        """Serve HTTP requests until the process stops."""
        self._logger.info(
            "HTTP server started | host=%s | port=%s",
            self._config.host,
            self._config.port,
        )
        self._server.serve_forever()

    def close(self) -> None:
        """Release the underlying server socket."""
        self._logger.info(
            "HTTP server stopping | host=%s | port=%s",
            self._config.host,
            self._config.port,
        )
        self._server.server_close()
        self._logger.info("HTTP server stopped")
