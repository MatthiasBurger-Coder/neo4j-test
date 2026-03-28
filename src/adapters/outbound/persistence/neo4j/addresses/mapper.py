"""Mappers for translating Neo4j address records into domain objects."""

from src.adapters.outbound.persistence.neo4j.addresses.read_model import AddressReadModel
from src.adapters.outbound.persistence.neo4j.repository.result import CypherRow, require_row_value
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.shared.graph.model.node_id import NodeId


class Neo4jAddressReadModelMapper:
    """Maps plain Neo4j result rows to address read models."""

    def map(self, *, statement_name: str, row: CypherRow) -> AddressReadModel:
        """Create an address read model from a materialized row."""
        return AddressReadModel(
            address_id=str(
                require_row_value(
                    statement_name=statement_name,
                    row=row,
                    field_name="address_id",
                )
            ),
            house_number=str(
                require_row_value(
                    statement_name=statement_name,
                    row=row,
                    field_name="house_number",
                )
            ),
            latitude=_to_optional_float(row.get("latitude")),
            longitude=_to_optional_float(row.get("longitude")),
        )


class AddressReadModelToDomainMapper:
    """Maps address read models to the pure address domain object."""

    def map(self, read_model: AddressReadModel) -> Address:
        """Create the domain address from the persisted read model."""
        return Address(
            id=NodeId(read_model.address_id),
            house_number=read_model.house_number,
            geo_location=_GEO_LOCATION_FACTORIES.get(
                (read_model.latitude is None, read_model.longitude is None),
                _raise_incomplete_geo_location,
            )(read_model.latitude, read_model.longitude),
        )


class Neo4jAddressRecordMapper:
    """Maps Neo4j execution rows to domain addresses through read models."""

    def __init__(
        self,
        *,
        read_model_mapper: Neo4jAddressReadModelMapper | None = None,
        domain_mapper: AddressReadModelToDomainMapper | None = None,
    ) -> None:
        self._read_model_mapper = read_model_mapper or Neo4jAddressReadModelMapper()
        self._domain_mapper = domain_mapper or AddressReadModelToDomainMapper()

    def map_one(self, *, statement_name: str, row: CypherRow) -> Address:
        """Map a single execution row to the domain address."""
        return self._domain_mapper.map(
            self._read_model_mapper.map(statement_name=statement_name, row=row)
        )

    def map_all(self, *, statement_name: str, rows: tuple[CypherRow, ...]) -> tuple[Address, ...]:
        """Map all execution rows to domain addresses."""
        return tuple(
            self.map_one(statement_name=statement_name, row=row)
            for row in rows
        )


def _to_optional_float(value: object) -> float | None:
    return None if value is None else float(value)


def _return_no_geo_location(latitude: float | None, longitude: float | None) -> GeoLocation | None:
    del latitude, longitude
    return None


def _return_complete_geo_location(latitude: float | None, longitude: float | None) -> GeoLocation:
    if latitude is None or longitude is None:
        raise ValueError("Geo location requires both latitude and longitude")
    return GeoLocation(latitude=latitude, longitude=longitude)


def _raise_incomplete_geo_location(latitude: float | None, longitude: float | None) -> GeoLocation | None:
    raise ValueError(
        "Address geo location must provide both latitude and longitude or neither "
        f"(latitude={latitude!r}, longitude={longitude!r})"
    )


_GEO_LOCATION_FACTORIES = {
    (True, True): _return_no_geo_location,
    (False, False): _return_complete_geo_location,
}
