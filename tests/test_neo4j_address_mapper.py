"""Unit tests for Neo4j address mapping components."""

import unittest

from src.adapters.outbound.persistence.neo4j.addresses.mapper import (
    AddressReadModelToDomainMapper,
    Neo4jAddressReadModelMapper,
    Neo4jAddressRecordMapper,
)
from src.adapters.outbound.persistence.neo4j.addresses.read_model import AddressReadModel


class Neo4jAddressMapperTest(unittest.TestCase):
    def test_read_model_mapper_maps_complete_row(self) -> None:
        mapper = Neo4jAddressReadModelMapper()

        result = mapper.map(
            statement_name="address.find_by_criteria",
            row={
                "address_id": "addr-1",
                "house_number": "42A",
                "latitude": 52.52,
                "longitude": 13.405,
            },
        )

        self.assertEqual("addr-1", result.address_id)
        self.assertEqual("42A", result.house_number)
        self.assertEqual(52.52, result.latitude)
        self.assertEqual(13.405, result.longitude)

    def test_read_model_mapper_raises_for_missing_required_field(self) -> None:
        mapper = Neo4jAddressReadModelMapper()

        with self.assertRaises(ValueError) as raised_error:
            mapper.map(
                statement_name="address.find_by_criteria",
                row={
                    "address_id": "addr-1",
                    "latitude": 52.52,
                    "longitude": 13.405,
                },
            )

        self.assertIn("required field 'house_number'", str(raised_error.exception))

    def test_domain_mapper_maps_address_without_geo_location(self) -> None:
        mapper = AddressReadModelToDomainMapper()

        result = mapper.map(
            AddressReadModel(
                address_id="addr-1",
                house_number="42A",
                latitude=None,
                longitude=None,
            )
        )

        self.assertEqual("addr-1", result.id.value)
        self.assertEqual("42A", result.house_number)
        self.assertIsNone(result.geo_location)

    def test_domain_mapper_raises_for_partial_geo_location(self) -> None:
        mapper = AddressReadModelToDomainMapper()

        with self.assertRaises(ValueError) as raised_error:
            mapper.map(
                AddressReadModel(
                    address_id="addr-1",
                    house_number="42A",
                    latitude=52.52,
                    longitude=None,
                )
            )

        self.assertIn("must provide both latitude and longitude or neither", str(raised_error.exception))

    def test_record_mapper_maps_multiple_rows(self) -> None:
        mapper = Neo4jAddressRecordMapper()

        result = mapper.map_all(
            statement_name="address.find_by_criteria",
            rows=(
                {
                    "address_id": "addr-1",
                    "house_number": "42A",
                    "latitude": None,
                    "longitude": None,
                },
                {
                    "address_id": "addr-2",
                    "house_number": "43",
                    "latitude": 52.53,
                    "longitude": 13.41,
                },
            ),
        )

        self.assertEqual(("addr-1", "addr-2"), tuple(address.id.value for address in result))
        self.assertEqual(("42A", "43"), tuple(address.house_number for address in result))


if __name__ == "__main__":
    unittest.main()
