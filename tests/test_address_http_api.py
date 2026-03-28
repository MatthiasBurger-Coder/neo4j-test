"""HTTP endpoint tests for the JSON-only address API."""

import io
import json
import unittest

from src.application.addresses.address_create_command import AddressCreateCommand
from src.application.addresses.address_create_service import (
    AddressCreateOperationError,
    AddressCreateValidationError,
)
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


class _FakeAddressCreateService:
    def __init__(self, *, address: Address | None = None, error: Exception | None = None) -> None:
        self._address = address
        self._error = error
        self.last_command: AddressCreateCommand | None = None

    def create_address(self, command: AddressCreateCommand) -> Address:
        self.last_command = command
        if self._error is not None:
            raise self._error
        if self._address is None:
            raise AssertionError("A created address must be configured for HTTP API tests")
        return self._address


class AddressHttpApiTest(unittest.TestCase):
    def test_get_addresses_returns_json_list(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(
                addresses=(
                    Address(id=NodeId("addr-1"), house_number="42A"),
                    Address(
                        id=NodeId("addr-2"),
                        house_number="43",
                        geo_location=GeoLocation(latitude=52.53, longitude=13.41),
                    ),
                )
            ),
            create_service=_FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        status, headers, body = _invoke_wsgi(app, method="GET", path="/addresses")

        self.assertEqual("200 OK", status)
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])
        self.assertEqual(["addr-1", "addr-2"], [entry["id"] for entry in body])

    def test_get_address_by_id_returns_json_object(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(address=Address(id=NodeId("addr-1"), house_number="42A")),
            create_service=_FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        status, headers, body = _invoke_wsgi(app, method="GET", path="/addresses/addr-1")

        self.assertEqual("200 OK", status)
        self.assertEqual("addr-1", body["id"])
        self.assertIsNone(body["geo_location"])
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])

    def test_get_address_by_id_returns_not_found(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(address=None),
            create_service=_FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses/missing")

        self.assertEqual("404 Not Found", status)
        self.assertEqual("address_not_found", body["error"]["code"])

    def test_get_addresses_returns_empty_json_list(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(addresses=()),
            create_service=_FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses")

        self.assertEqual("200 OK", status)
        self.assertEqual([], body)

    def test_get_address_by_id_returns_bad_request_for_invalid_identifier(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(
                error=AddressQueryValidationError("Address id must not be blank")
            ),
            create_service=_FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses/   ")

        self.assertEqual("400 Bad Request", status)
        self.assertEqual("invalid_address_id", body["error"]["code"])

    def test_get_addresses_returns_internal_error_for_technical_failure(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(error=RuntimeError("database unavailable")),
            create_service=_FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        status, _, body = _invoke_wsgi(app, method="GET", path="/addresses")

        self.assertEqual("500 Internal Server Error", status)
        self.assertEqual("internal_error", body["error"]["code"])

    def test_post_addresses_returns_created_json_payload(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            create_service=_FakeAddressCreateService(
                address=Address(
                    id=NodeId("addr-1"),
                    house_number="42A",
                    geo_location=GeoLocation(latitude=52.52, longitude=13.405),
                )
            ),
        )

        status, headers, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=b'{"house_number":"42A","geo_location":{"latitude":52.52,"longitude":13.405}}',
            content_type="application/json",
        )

        self.assertEqual("201 Created", status)
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])
        self.assertEqual("addr-1", body["id"])
        self.assertEqual("42A", body["house_number"])
        self.assertEqual(52.52, body["geo_location"]["latitude"])

    def test_post_addresses_rejects_invalid_json(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            create_service=_FakeAddressCreateService(address=_create_address("addr-1", "42A")),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=b'{"house_number":',
            content_type="application/json",
        )

        self.assertEqual("400 Bad Request", status)
        self.assertEqual("invalid_json", body["error"]["code"])

    def test_post_addresses_rejects_missing_required_field(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            create_service=_FakeAddressCreateService(address=_create_address("addr-1", "42A")),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=b"{}",
            content_type="application/json",
        )

        self.assertEqual("400 Bad Request", status)
        self.assertEqual("missing_required_field", body["error"]["code"])

    def test_post_addresses_rejects_domain_invalid_data(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            create_service=_FakeAddressCreateService(
                error=AddressCreateValidationError("Address house_number must not be blank")
            ),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=b'{"house_number":"   "}',
            content_type="application/json",
        )

        self.assertEqual("422 Unprocessable Content", status)
        self.assertEqual("invalid_address", body["error"]["code"])

    def test_post_addresses_returns_internal_error_for_technical_failure(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            create_service=_FakeAddressCreateService(
                error=AddressCreateOperationError("Address could not be created")
            ),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=b'{"house_number":"42A"}',
            content_type="application/json",
        )

        self.assertEqual("500 Internal Server Error", status)
        self.assertEqual("internal_error", body["error"]["code"])


def _create_http_api(*, query_service: _FakeAddressReadService, create_service: _FakeAddressCreateService):
    return create_http_api(
        services=ApplicationServices(
            addresses=AddressServices(query=query_service, create=create_service)
        )
    )


def _invoke_wsgi(
    app,
    *,
    method: str,
    path: str,
    body: bytes = b"",
    content_type: str | None = None,
):
    response_status: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        response_status["status"] = status
        response_status["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    if content_type is not None:
        environ["CONTENT_TYPE"] = content_type

    payload = b"".join(app(environ, start_response))
    return (
        response_status["status"],
        response_status["headers"],
        json.loads(payload.decode("utf-8")),
    )


def _create_address(address_id: str, house_number: str) -> Address:
    return Address(id=NodeId(address_id), house_number=house_number)


if __name__ == "__main__":
    unittest.main()
