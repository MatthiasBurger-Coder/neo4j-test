"""HTTP controller for address read requests."""

import logging
from http import HTTPStatus

from src.adapters.inbound.http.address_create_request_mapper import (
    AddressCreateHttpRequestError,
    AddressCreateHttpRequestMapper,
)
from src.adapters.inbound.http.address_response_mapper import AddressHttpResponseMapper
from src.adapters.inbound.http.request import HttpRequest
from src.adapters.inbound.http.response import (
    JsonResponse,
    json_bad_request,
    json_created,
    json_internal_server_error,
    json_not_found,
    json_ok,
    json_unprocessable_entity,
    json_unsupported_media_type,
)
from src.application.addresses.address_create_port import AddressCreatePort
from src.application.addresses.address_create_service import (
    AddressCreateOperationError,
    AddressCreateValidationError,
)
from src.application.addresses.address_query_service import AddressQueryValidationError
from src.application.addresses.address_read_port import AddressReadPort


class AddressHttpController:
    """Handles JSON-only HTTP requests for address read use cases."""

    def __init__(
        self,
        address_read_service: AddressReadPort,
        address_create_service: AddressCreatePort,
        *,
        request_mapper: AddressCreateHttpRequestMapper | None = None,
        response_mapper: AddressHttpResponseMapper | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._address_read_service = address_read_service
        self._address_create_service = address_create_service
        self._request_mapper = request_mapper or AddressCreateHttpRequestMapper()
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

    def create_address(self, request: HttpRequest) -> JsonResponse:
        """Handle the create-address endpoint."""
        try:
            command = self._request_mapper.map(request)
            address = self._address_create_service.create_address(command)
        except AddressCreateHttpRequestError as error:
            self._logger.warning(
                "HTTP address create rejected | status_code=%s | code=%s | error=%s",
                error.status_code,
                error.code,
                error.message,
            )
            return _REQUEST_ERROR_RESPONSES[error.status_code](code=error.code, message=error.message)
        except AddressCreateValidationError as error:
            self._logger.warning("HTTP address create rejected | error=%s", error)
            return json_unprocessable_entity(code="invalid_address", message=str(error))
        except AddressCreateOperationError as error:
            self._logger.error("HTTP address create failed | error=%s", error)
            return json_internal_server_error()
        except Exception as error:
            self._logger.error(
                "HTTP address create failed | error_type=%s | error=%s",
                error.__class__.__name__,
                error,
            )
            return json_internal_server_error()

        return json_created(self._response_mapper.map_created_context(address))


_REQUEST_ERROR_RESPONSES = {
    HTTPStatus.BAD_REQUEST: json_bad_request,
    HTTPStatus.UNSUPPORTED_MEDIA_TYPE: json_unsupported_media_type,
}
