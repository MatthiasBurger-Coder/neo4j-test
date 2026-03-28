"""WSGI application for the JSON-only HTTP adapter."""

import json
import logging
from collections.abc import Callable, Iterable
from typing import BinaryIO

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
            headers=_extract_headers(environ),
            body=_read_request_body(environ),
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


def _extract_headers(environ: dict[str, object]) -> dict[str, str]:
    headers = {
        key[5:].replace("_", "-").lower(): str(value)
        for key, value in environ.items()
        if key.startswith("HTTP_")
    }
    if "CONTENT_TYPE" in environ:
        headers["content-type"] = str(environ["CONTENT_TYPE"])
    if "CONTENT_LENGTH" in environ:
        headers["content-length"] = str(environ["CONTENT_LENGTH"])
    return headers


def _read_request_body(environ: dict[str, object]) -> bytes:
    body_stream = environ.get("wsgi.input")
    if body_stream is None:
        return b""

    content_length = _parse_content_length(environ.get("CONTENT_LENGTH"))
    if content_length <= 0:
        return b""

    body = _require_binary_stream(body_stream).read(content_length)
    return body if isinstance(body, bytes) else bytes(body)


def _parse_content_length(raw_content_length: object) -> int:
    if raw_content_length is None:
        return 0

    try:
        return max(0, int(str(raw_content_length)))
    except ValueError:
        return 0


def _require_binary_stream(body_stream: object) -> BinaryIO:
    if not hasattr(body_stream, "read"):
        raise TypeError("WSGI input stream must provide a read method")
    return body_stream
