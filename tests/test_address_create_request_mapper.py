"""Unit tests for the address create HTTP request mapper."""

import unittest

from src.adapters.inbound.http.address_create_request_mapper import (
    AddressCreateHttpRequestError,
    AddressCreateHttpRequestMapper,
)
from src.adapters.inbound.http.request import HttpRequest


class AddressCreateHttpRequestMapperTest(unittest.TestCase):
    def test_map_returns_command_for_valid_full_request(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        result = mapper.map(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=(
                    b'{"address":{"house_number":"12A","geo_location":{"latitude":48.137154,"longitude":11.576124}},'
                    b'"street":{"name":"Marienplatz"},'
                    b'"city":{"name":"Munich","country":"Germany","postal_code":"80331"},'
                    b'"building":{"name":"Town Hall","geo_location":{"latitude":48.1372,"longitude":11.5759}},'
                    b'"units":[{"unit_type":"ENTRANCE","value":"North"},{"unit_type":"FLOOR","value":"3"}],'
                    b'"unit_hierarchy":[{"parent_ref":"ENTRANCE:North","child_ref":"FLOOR:3"}],'
                    b'"assignments":[{"related_entity":{"entity_type":"PERSON","entity_id":"person-123"},'
                    b'"relation_type":"RESIDENCE","valid_from":"2024-01-01T00:00:00Z","source":"registry","note":"Primary residence"}]}'
                ),
            )
        )

        self.assertEqual("12A", result.address.house_number)
        self.assertEqual(48.137154, result.address.geo_location.latitude)
        self.assertEqual("Marienplatz", result.street.name)
        self.assertEqual("Germany", result.city.country)
        self.assertEqual("Town Hall", result.building.name)
        self.assertEqual("ENTRANCE", result.units[0].unit_type)
        self.assertEqual("ENTRANCE:North", result.unit_hierarchy[0].parent_ref)
        self.assertEqual("PERSON", result.assignments[0].related_entity.entity_type)

    def test_map_rejects_unsupported_media_type(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "text/plain"},
                    body=b"{}",
                )
            )

        self.assertEqual(415, raised_error.exception.status_code)
        self.assertEqual("unsupported_media_type", raised_error.exception.code)

    def test_map_rejects_invalid_json(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "application/json"},
                    body=b'{"address":',
                )
            )

        self.assertEqual(400, raised_error.exception.status_code)
        self.assertEqual("invalid_json", raised_error.exception.code)

    def test_map_rejects_missing_required_nested_field(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "application/json"},
                    body=b'{"street":{"name":"Marienplatz"},"city":{"name":"Munich","country":"Germany"}}',
                )
            )

        self.assertEqual("missing_required_field", raised_error.exception.code)
        self.assertIn("address", raised_error.exception.message)

    def test_map_rejects_invalid_units_payload_type(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "application/json"},
                    body=(
                        b'{"address":{"house_number":"12A"},'
                        b'"street":{"name":"Marienplatz"},'
                        b'"city":{"name":"Munich","country":"Germany"},'
                        b'"units":{"unit_type":"ENTRANCE","value":"North"}}'
                    ),
                )
            )

        self.assertEqual("invalid_field_type", raised_error.exception.code)

    def test_map_rejects_invalid_geo_location_payload(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "application/json"},
                    body=(
                        b'{"address":{"house_number":"12A","geo_location":{"latitude":"north","longitude":11.576124}},'
                        b'"street":{"name":"Marienplatz"},'
                        b'"city":{"name":"Munich","country":"Germany"}}'
                    ),
                )
            )

        self.assertEqual("invalid_field_type", raised_error.exception.code)


if __name__ == "__main__":
    unittest.main()
