"""WSGI application for the JSON-only HTTP adapter."""

import json
import logging
from collections.abc import Callable, Iterable

from src.adapters.inbound.http.request import HttpRequest
from src.adapters.inbound.http.response import JsonResponse, json_internal_server_error
from src.adapters.inbound.http.router import HttpRouter


StartResponse = Callable[[str, list[tuple[str, str]]], None]


class JsonWsgiApplication:
    """Converts WSGI requests into JSON-only HTTP responses."""

    def __init__(
        self,
        *,
        router: HttpRouter,
        logger: logging.Logger | None = None,
    ) -> None:
        self._router = router
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def __call__(self, environ: dict[str, object], start_response: StartResponse) -> Iterable[bytes]:
        request = HttpRequest(
            method=str(environ.get("REQUEST_METHOD", "GET")),
            path=str(environ.get("PATH_INFO", "/")),
        )
        self._logger.info("HTTP request started | method=%s | path=%s", request.method, request.path)

        try:
            response = self._router.route(request)
        except Exception as error:
            self._logger.error(
                "HTTP request failed | method=%s | path=%s | error_type=%s | error=%s",
                request.method,
                request.path,
                error.__class__.__name__,
                error,
            )
            response = json_internal_server_error()

        payload = json.dumps(response.payload).encode("utf-8")
        headers = [*response.headers, ("Content-Length", str(len(payload)))]
        start_response(response.status_line, headers)
        self._logger.info(
            "HTTP request completed | method=%s | path=%s | status=%s",
            request.method,
            request.path,
            response.status_code,
        )
        return [payload]
