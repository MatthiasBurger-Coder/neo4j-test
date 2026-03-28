"""HTTP API wiring exposed by the bootstrap context."""

from src.adapters.inbound.http.address_controller import AddressHttpController
from src.adapters.inbound.http.address_response_mapper import AddressHttpResponseMapper
from src.adapters.inbound.http.router import (
    HttpRouter,
    SingleParameterRouteStrategy,
    StaticRouteStrategy,
)
from src.adapters.inbound.http.wsgi_application import JsonWsgiApplication
from src.infrastructure.bootstrap.application_services import ApplicationServices
from src.infrastructure.logging.logger_factory import LoggerFactory


def create_http_api(*, services: ApplicationServices) -> JsonWsgiApplication:
    """Create the JSON-only HTTP API for the application."""
    controller = AddressHttpController(
        services.addresses.query,
        response_mapper=AddressHttpResponseMapper(),
        logger=LoggerFactory.get_logger(AddressHttpController.__name__),
    )
    router = HttpRouter(
        routes=(
            StaticRouteStrategy(
                method="GET",
                path="/addresses",
                handler=lambda path_parameters: _get_addresses(controller, path_parameters),
            ),
            SingleParameterRouteStrategy(
                method="GET",
                prefix="/addresses",
                parameter_name="address_id",
                handler=lambda path_parameters: _get_address_by_id(controller, path_parameters),
            ),
        )
    )
    return JsonWsgiApplication(
        router=router,
        logger=LoggerFactory.get_logger(JsonWsgiApplication.__name__),
    )


def _get_addresses(
    controller: AddressHttpController,
    path_parameters: dict[str, str],
):
    del path_parameters
    return controller.get_addresses()


def _get_address_by_id(
    controller: AddressHttpController,
    path_parameters: dict[str, str],
):
    return controller.get_address_by_id(path_parameters["address_id"])
