"""HTTP controller for address read requests."""

import logging

from src.adapters.inbound.http.address_response_mapper import AddressHttpResponseMapper
from src.adapters.inbound.http.response import (
    JsonResponse,
    json_bad_request,
    json_internal_server_error,
    json_not_found,
    json_ok,
)
from src.application.addresses.address_query_service import AddressQueryValidationError
from src.application.addresses.address_read_port import AddressReadPort


class AddressHttpController:
    """Handles JSON-only HTTP requests for address read use cases."""

    def __init__(
        self,
        address_read_service: AddressReadPort,
        *,
        response_mapper: AddressHttpResponseMapper | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._address_read_service = address_read_service
        self._response_mapper = response_mapper or AddressHttpResponseMapper()
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def get_addresses(self) -> JsonResponse:
        """Handle the collection read endpoint."""
        try:
            return json_ok(self._response_mapper.map_many(self._address_read_service.get_all_addresses()))
        except Exception as error:
            self._logger.error("HTTP address list failed | error_type=%s | error=%s", error.__class__.__name__, error)
            return json_internal_server_error()

    def get_address_by_id(self, address_id: str) -> JsonResponse:
        """Handle the single-address read endpoint."""
        try:
            address = self._address_read_service.get_address_by_id(address_id)
        except AddressQueryValidationError as error:
            self._logger.warning(
                "HTTP address read rejected | address_id=%s | error=%s",
                address_id,
                error,
            )
            return json_bad_request(code="invalid_address_id", message=str(error))
        except Exception as error:
            self._logger.error(
                "HTTP address read failed | address_id=%s | error_type=%s | error=%s",
                address_id,
                error.__class__.__name__,
                error,
            )
            return json_internal_server_error()

        if address is None:
            return json_not_found(code="address_not_found", message="Address not found")

        return json_ok(self._response_mapper.map_one(address))
