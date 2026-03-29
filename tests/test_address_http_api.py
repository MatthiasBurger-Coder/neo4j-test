"""HTTP endpoint tests for the JSON-only address API."""

from datetime import datetime, timezone
import io
import json
import unittest

from src.application.addresses.address_context import AddressContextDraft, CreatedAddressContext
from src.application.addresses.address_create_service import AddressCreateService
from src.application.addresses.address_write_port import AddressWriteError
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.address_assignment import AddressAssignment
from src.domain.addresses.model.address_has_unit import AddressHasUnit
from src.domain.addresses.model.address_in_building import AddressInBuilding
from src.domain.addresses.model.address_on_street import AddressOnStreet
from src.domain.addresses.model.address_relation_type import AddressRelationType
from src.domain.addresses.model.address_unit import AddressUnit
from src.domain.addresses.model.address_unit_type import AddressUnitType
from src.domain.addresses.model.address_unit_within_unit import AddressUnitWithinUnit
from src.domain.addresses.model.building import Building
from src.domain.addresses.model.city import City
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.addresses.model.related_entity_ref import RelatedEntityRef, RelatedEntityType
from src.domain.addresses.model.street import Street
from src.domain.addresses.model.street_in_city import StreetInCity
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.graph.model.relationship_id import RelationshipId
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


class _PreparedAddressWritePort:
    def __init__(self, *, created_context: CreatedAddressContext | None = None, error: Exception | None = None) -> None:
        self._created_context = created_context
        self._error = error
        self.last_context: AddressContextDraft | None = None

    def create_address(self, address_context: AddressContextDraft) -> CreatedAddressContext:
        self.last_context = address_context
        if self._error is not None:
            raise self._error
        if self._created_context is None:
            raise AssertionError("A created context must be configured for HTTP API tests")
        return self._created_context


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
            write_port=_PreparedAddressWritePort(created_context=_create_created_context()),
        )

        status, headers, body = _invoke_wsgi(app, method="GET", path="/addresses")

        self.assertEqual("200 OK", status)
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])
        self.assertEqual(["addr-1", "addr-2"], [entry["id"] for entry in body])

    def test_get_address_by_id_returns_json_object(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(address=Address(id=NodeId("addr-1"), house_number="42A")),
            write_port=_PreparedAddressWritePort(created_context=_create_created_context()),
        )

        status, headers, body = _invoke_wsgi(app, method="GET", path="/addresses/addr-1")

        self.assertEqual("200 OK", status)
        self.assertEqual("addr-1", body["id"])
        self.assertIsNone(body["geo_location"])
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])

    def test_post_addresses_returns_created_full_context(self) -> None:
        write_port = _PreparedAddressWritePort(created_context=_create_created_context())
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            write_port=write_port,
        )

        status, headers, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=_full_request_body(),
            content_type="application/json",
        )

        self.assertEqual("201 Created", status)
        self.assertEqual("application/json; charset=utf-8", headers["Content-Type"])
        self.assertEqual("addr-1", body["address"]["id"])
        self.assertEqual("street-1", body["street"]["id"])
        self.assertEqual("city-1", body["city"]["id"])
        self.assertEqual("building-1", body["building"]["id"])
        self.assertEqual("ENTRANCE", body["units"][0]["unit_type"])
        self.assertEqual("PERSON", body["assignments"][0]["related_entity"]["entity_type"])
        self.assertEqual("Marienplatz", write_port.last_context.street.name)
        self.assertEqual("ENTRANCE:North", write_port.last_context.units[0].reference)

    def test_post_addresses_rejects_invalid_json(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            write_port=_PreparedAddressWritePort(created_context=_create_created_context()),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=b'{"address":',
            content_type="application/json",
        )

        self.assertEqual("400 Bad Request", status)
        self.assertEqual("invalid_json", body["error"]["code"])

    def test_post_addresses_rejects_missing_required_field(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            write_port=_PreparedAddressWritePort(created_context=_create_created_context()),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=b'{"street":{"name":"Marienplatz"},"city":{"name":"Munich","country":"Germany"}}',
            content_type="application/json",
        )

        self.assertEqual("400 Bad Request", status)
        self.assertEqual("missing_required_field", body["error"]["code"])

    def test_post_addresses_rejects_invalid_enum_value(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            write_port=_PreparedAddressWritePort(created_context=_create_created_context()),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=_full_request_body().replace(b'"ENTRANCE"', b'"INVALID_ENUM"', 1),
            content_type="application/json",
        )

        self.assertEqual("422 Unprocessable Content", status)
        self.assertEqual("invalid_address", body["error"]["code"])

    def test_post_addresses_rejects_invalid_geo_location(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            write_port=_PreparedAddressWritePort(created_context=_create_created_context()),
        )

        invalid_body = _full_request_body().replace(b"48.137154", b"120.0", 1)
        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=invalid_body,
            content_type="application/json",
        )

        self.assertEqual("422 Unprocessable Content", status)
        self.assertEqual("invalid_address", body["error"]["code"])

    def test_post_addresses_rejects_invalid_assignment_window(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            write_port=_PreparedAddressWritePort(created_context=_create_created_context()),
        )

        invalid_body = _full_request_body().replace(
            b'"valid_from":"2024-01-01T00:00:00Z"',
            b'"valid_from":"2024-02-01T00:00:00Z","valid_to":"2024-01-01T00:00:00Z"',
            1,
        )
        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=invalid_body,
            content_type="application/json",
        )

        self.assertEqual("422 Unprocessable Content", status)
        self.assertEqual("invalid_address", body["error"]["code"])

    def test_post_addresses_returns_internal_error_for_technical_failure(self) -> None:
        app = _create_http_api(
            query_service=_FakeAddressReadService(),
            write_port=_PreparedAddressWritePort(error=AddressWriteError("database unavailable")),
        )

        status, _, body = _invoke_wsgi(
            app,
            method="POST",
            path="/addresses",
            body=_full_request_body(),
            content_type="application/json",
        )

        self.assertEqual("500 Internal Server Error", status)
        self.assertEqual("internal_error", body["error"]["code"])


def _create_http_api(*, query_service: _FakeAddressReadService, write_port: _PreparedAddressWritePort):
    return create_http_api(
        services=ApplicationServices(
            addresses=AddressServices(
                query=query_service,
                create=AddressCreateService(write_port),
            )
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


def _full_request_body() -> bytes:
    return (
        b'{"address":{"house_number":"12A","geo_location":{"latitude":48.137154,"longitude":11.576124}},'
        b'"street":{"name":"Marienplatz"},'
        b'"city":{"name":"Munich","country":"Germany","postal_code":"80331"},'
        b'"building":{"name":"Town Hall","geo_location":{"latitude":48.1372,"longitude":11.5759}},'
        b'"units":[{"unit_type":"ENTRANCE","value":"North"},{"unit_type":"FLOOR","value":"3"},{"unit_type":"APARTMENT","value":"12"}],'
        b'"unit_hierarchy":[{"parent_ref":"ENTRANCE:North","child_ref":"FLOOR:3"},{"parent_ref":"FLOOR:3","child_ref":"APARTMENT:12"}],'
        b'"assignments":[{"related_entity":{"entity_type":"PERSON","entity_id":"person-123"},'
        b'"relation_type":"RESIDENCE","valid_from":"2024-01-01T00:00:00Z","source":"registry","note":"Primary residence"}]}'
    )


def _create_created_context() -> CreatedAddressContext:
    address = Address(
        id=NodeId("addr-1"),
        house_number="12A",
        geo_location=GeoLocation(latitude=48.137154, longitude=11.576124),
    )
    street = Street(id=NodeId("street-1"), name="Marienplatz")
    city = City(id=NodeId("city-1"), name="Munich", country="Germany", postal_code="80331")
    building = Building(
        id=NodeId("building-1"),
        name="Town Hall",
        geo_location=GeoLocation(latitude=48.1372, longitude=11.5759),
    )
    units = (
        AddressUnit(id=NodeId("unit-1"), unit_type=AddressUnitType.ENTRANCE, value="North"),
        AddressUnit(id=NodeId("unit-2"), unit_type=AddressUnitType.FLOOR, value="3"),
        AddressUnit(id=NodeId("unit-3"), unit_type=AddressUnitType.APARTMENT, value="12"),
    )
    return CreatedAddressContext(
        address=address,
        street=street,
        city=city,
        address_on_street=AddressOnStreet(
            id=RelationshipId("rel-address-street-1"),
            address_id=address.id,
            street_id=street.id,
        ),
        street_in_city=StreetInCity(
            id=RelationshipId("rel-street-city-1"),
            street_id=street.id,
            city_id=city.id,
        ),
        building=building,
        address_in_building=AddressInBuilding(
            id=RelationshipId("rel-address-building-1"),
            address_id=address.id,
            building_id=building.id,
        ),
        units=units,
        address_has_units=(
            AddressHasUnit(id=RelationshipId("rel-address-unit-1"), address_id=address.id, address_unit_id=units[0].id),
            AddressHasUnit(id=RelationshipId("rel-address-unit-2"), address_id=address.id, address_unit_id=units[1].id),
            AddressHasUnit(id=RelationshipId("rel-address-unit-3"), address_id=address.id, address_unit_id=units[2].id),
        ),
        unit_hierarchy=(
            AddressUnitWithinUnit(
                id=RelationshipId("rel-unit-hierarchy-1"),
                parent_unit_id=units[0].id,
                child_unit_id=units[1].id,
            ),
            AddressUnitWithinUnit(
                id=RelationshipId("rel-unit-hierarchy-2"),
                parent_unit_id=units[1].id,
                child_unit_id=units[2].id,
            ),
        ),
        assignments=(
            AddressAssignment(
                id=RelationshipId("rel-assignment-1"),
                related_entity=RelatedEntityRef(
                    entity_type=RelatedEntityType.PERSON,
                    entity_id=NodeId("person-123"),
                ),
                address_id=address.id,
                relation_type=AddressRelationType.RESIDENCE,
                valid_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
                source="registry",
                note="Primary residence",
            ),
        ),
    )


if __name__ == "__main__":
    unittest.main()
