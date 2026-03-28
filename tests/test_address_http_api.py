"""HTTP endpoint tests for the JSON-only address API."""

import json
import unittest

from src.application.addresses.address_query_service import AddressQueryValidationError
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.shared.graph.model.node_id import NodeId
from src.infrastructure.bootstrap.application_services import AddressServices, ApplicationServices
from src.infrastructure.bootstrap.http_api import create_http_api


class _FakeAddressReadService:
    def __init__(
        self,
        *,
        address: Address | None = None,
        addresses: tuple[Address, ...] = (),
        error: Exception | None = None,
    ) -> None:
        self._address = address
        self._addresses = addresses
        self._error = error

    def get_address_by_id(self, address_id: str) -> Address | None:
        del address_id
        if self._error is not None:
            raise self._error
        return self._address

    def get_all_addresses(self) -> tuple[Address, ...]:
        if self._error is not None:
            raise self._error
        return self._addresses


class AddressHttpApiTest(unittest.TestCase):
    def test_get_addresses_returns_json_list(self) -> None:
        app = _create_http_api(
            _FakeAddressReadService(
                addresses=(
                    Address(id=NodeId("addr-1"), house_number="42A"),
                    Address(
                        id=NodeId("addr-2"),
                        house_number="43",
                        geo_location=GeoLocation(latitude=52.53, longitude=13.41),
                    ),
                )
            )
        )

        status, headers, body = _invoke_wsgi(app, method="GET", path="/addresses")

        self.assertEqual("200 OK", status)
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])
        self.assertEqual(["addr-1", "addr-2"], [entry["id"] for entry in body])

    def test_get_address_by_id_returns_json_object(self) -> None:
        app = _create_http_api(
            _FakeAddressReadService(address=Address(id=NodeId("addr-1"), house_number="42A"))
        )

        status, headers, body = _invoke_wsgi(app, method="GET", path="/addresses/addr-1")

        self.assertEqual("200 OK", status)
        self.assertEqual("addr-1", body["id"])
        self.assertIsNone(body["geo_location"])
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])

    def test_get_address_by_id_returns_not_found(self) -> None:
        app = _create_http_api(_FakeAddressReadService(address=None))

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses/missing")

        self.assertEqual("404 Not Found", status)
        self.assertEqual("address_not_found", body["error"]["code"])

    def test_get_addresses_returns_empty_json_list(self) -> None:
        app = _create_http_api(_FakeAddressReadService(addresses=()))

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses")

        self.assertEqual("200 OK", status)
        self.assertEqual([], body)

    def test_get_address_by_id_returns_bad_request_for_invalid_identifier(self) -> None:
        app = _create_http_api(
            _FakeAddressReadService(error=AddressQueryValidationError("Address id must not be blank"))
        )

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses/   ")

        self.assertEqual("400 Bad Request", status)
        self.assertEqual("invalid_address_id", body["error"]["code"])

    def test_get_addresses_returns_internal_error_for_technical_failure(self) -> None:
        app = _create_http_api(_FakeAddressReadService(error=RuntimeError("database unavailable")))

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses")

        self.assertEqual("500 Internal Server Error", status)
        self.assertEqual("internal_error", body["error"]["code"])


def _create_http_api(service: _FakeAddressReadService):
    return create_http_api(
        services=ApplicationServices(addresses=AddressServices(query=service))
    )


def _invoke_wsgi(app, *, method: str, path: str):
    response_status: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        response_status["status"] = status
        response_status["headers"] = dict(headers)

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": method,
                "PATH_INFO": path,
            },
            start_response,
        )
    )
    return (
        response_status["status"],
        response_status["headers"],
        json.loads(body.decode("utf-8")),
    )


if __name__ == "__main__":
    unittest.main()
