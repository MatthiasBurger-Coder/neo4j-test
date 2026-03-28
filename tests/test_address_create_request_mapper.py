"""Unit tests for the address create HTTP request mapper."""

import unittest

from src.adapters.inbound.http.address_create_request_mapper import (
    AddressCreateHttpRequestError,
    AddressCreateHttpRequestMapper,
)
from src.adapters.inbound.http.request import HttpRequest


class AddressCreateHttpRequestMapperTest(unittest.TestCase):
    def test_map_returns_command_for_valid_request(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        result = mapper.map(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=b'{"house_number":"42A","geo_location":{"latitude":52.52,"longitude":13.405}}',
            )
        )

        self.assertEqual("42A", result.house_number)
        self.assertEqual(52.52, result.latitude)
        self.assertEqual(13.405, result.longitude)

    def test_map_rejects_unsupported_media_type(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "text/plain"},
                    body=b'{"house_number":"42A"}',
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
                    body=b'{"house_number":',
                )
            )

        self.assertEqual(400, raised_error.exception.status_code)
        self.assertEqual("invalid_json", raised_error.exception.code)

    def test_map_rejects_missing_required_field(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "application/json"},
                    body=b"{}",
                )
            )

        self.assertEqual("missing_required_field", raised_error.exception.code)

    def test_map_rejects_invalid_geo_location_payload(self) -> None:
        mapper = AddressCreateHttpRequestMapper()

        with self.assertRaises(AddressCreateHttpRequestError) as raised_error:
            mapper.map(
                HttpRequest(
                    method="POST",
                    path="/addresses",
                    headers={"content-type": "application/json"},
                    body=b'{"house_number":"42A","geo_location":{"latitude":"north","longitude":13.405}}',
                )
            )

        self.assertEqual("invalid_field_type", raised_error.exception.code)


if __name__ == "__main__":
    unittest.main()
