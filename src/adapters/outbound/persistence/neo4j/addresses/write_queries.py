"""Cypher query definitions for address write operations."""

from src.adapters.outbound.persistence.neo4j.addresses.write_model import CreateAddressWriteModel
from src.adapters.outbound.persistence.neo4j.repository.contracts import CypherStatementBuilder
from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement


class CreateAddressStatementBuilder(CypherStatementBuilder[CreateAddressWriteModel]):
    """Builds the create-side address statement from the write model."""

    def build(self, request_model: CreateAddressWriteModel) -> CypherStatement:
        return CypherStatement(
            name="address.create",
            cypher=_ADDRESS_CREATE_QUERY.strip(),
            parameters={
                "address_id": request_model.address_id,
                "house_number": request_model.house_number,
                "latitude": request_model.latitude,
                "longitude": request_model.longitude,
            },
        )


_ADDRESS_CREATE_QUERY = """
CREATE (address:Address {
    id: $address_id,
    house_number: $house_number,
    latitude: $latitude,
    longitude: $longitude
})
RETURN
    address.id AS address_id,
    address.house_number AS house_number,
    address.latitude AS latitude,
    address.longitude AS longitude
"""
