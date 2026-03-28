"""Routing strategies for the lightweight HTTP adapter."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from src.adapters.inbound.http.request import HttpRequest
from src.adapters.inbound.http.response import JsonResponse, json_not_found


RouteHandler = Callable[[HttpRequest, dict[str, str]], JsonResponse]


@dataclass(frozen=True, slots=True)
class RouteMatch:
    """Represents a matched route and its extracted path parameters."""

    handler: RouteHandler
    path_parameters: dict[str, str]


class RouteStrategy(ABC):
    """Matches an incoming request against a route definition."""

    @abstractmethod
    def match(self, request: HttpRequest) -> RouteMatch | None:
        """Return the route match when the request fits the strategy."""


class StaticRouteStrategy(RouteStrategy):
    """Matches fixed paths without route parameters."""

    def __init__(self, *, method: str, path: str, handler: RouteHandler) -> None:
        self._method = method
        self._path = path
        self._handler = handler

    def match(self, request: HttpRequest) -> RouteMatch | None:
        return _STATIC_ROUTE_MATCHERS[(request.method == self._method, request.path == self._path)](self._handler)


class SingleParameterRouteStrategy(RouteStrategy):
    """Matches paths with exactly one trailing path parameter."""

    def __init__(
        self,
        *,
        method: str,
        prefix: str,
        parameter_name: str,
        handler: RouteHandler,
    ) -> None:
        self._method = method
        self._prefix = prefix.rstrip("/")
        self._parameter_name = parameter_name
        self._handler = handler

    def match(self, request: HttpRequest) -> RouteMatch | None:
        return _SINGLE_PARAMETER_ROUTE_MATCHERS[request.method == self._method](self, request.path)


class HttpRouter:
    """Dispatches requests through a strategy-based route registry."""

    def __init__(self, routes: tuple[RouteStrategy, ...]) -> None:
        self._routes = routes

    def route(self, request: HttpRequest) -> JsonResponse:
        """Resolve the request and invoke the matching route handler."""
        for route in self._routes:
            route_match = route.match(request)
            if route_match is not None:
                return route_match.handler(request, route_match.path_parameters)
        return json_not_found(code="route_not_found", message="Route not found")


def _return_static_route_match(handler: RouteHandler) -> RouteMatch:
    return RouteMatch(handler=handler, path_parameters={})


def _return_no_static_route_match(handler: RouteHandler) -> RouteMatch | None:
    del handler
    return None


def _match_single_parameter_route(strategy: SingleParameterRouteStrategy, path: str) -> RouteMatch | None:
    stripped_path = path.rstrip("/")
    prefix_with_separator = strategy._prefix + "/"
    if not stripped_path.startswith(prefix_with_separator):
        return None

    parameter_value = stripped_path.removeprefix(prefix_with_separator)
    return _SINGLE_PARAMETER_VALUE_MATCHERS["/" not in parameter_value and parameter_value != ""](
        strategy._handler,
        strategy._parameter_name,
        parameter_value,
    )


def _return_no_single_parameter_route_match(
    strategy: SingleParameterRouteStrategy,
    path: str,
) -> RouteMatch | None:
    del strategy, path
    return None


def _return_parameter_route_match(
    handler: RouteHandler,
    parameter_name: str,
    parameter_value: str,
) -> RouteMatch:
    return RouteMatch(handler=handler, path_parameters={parameter_name: parameter_value})


def _return_no_parameter_route_match(
    handler: RouteHandler,
    parameter_name: str,
    parameter_value: str,
) -> RouteMatch | None:
    del handler, parameter_name, parameter_value
    return None


_STATIC_ROUTE_MATCHERS = {
    (True, True): _return_static_route_match,
    (True, False): _return_no_static_route_match,
    (False, True): _return_no_static_route_match,
    (False, False): _return_no_static_route_match,
}

_SINGLE_PARAMETER_ROUTE_MATCHERS = {
    True: _match_single_parameter_route,
    False: _return_no_single_parameter_route_match,
}

_SINGLE_PARAMETER_VALUE_MATCHERS = {
    True: _return_parameter_route_match,
    False: _return_no_parameter_route_match,
}
