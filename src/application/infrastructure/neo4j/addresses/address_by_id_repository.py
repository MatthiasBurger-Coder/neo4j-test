"""Neo4j repository implementation for loading addresses by identifier."""

from src.application.domain.addresses.model.address import Address
from src.application.domain.addresses.model.geo_location import GeoLocation
from src.application.domain.addresses.port.address_by_id_repository import (
    AddressByIdRepositoryPort,
    FindAddressByIdQuery,
)
from src.application.domain.shared.graph.model.node_id import NodeId
from src.application.infrastructure.neo4j.repository.adapter import Neo4jReadRepositoryAdapter
from src.application.infrastructure.neo4j.repository.contracts import (
    CypherStatementBuilder,
    Neo4jRepositoryExecutorProtocol,
    Neo4jResultProjector,
)
from src.application.infrastructure.neo4j.repository.result import Neo4jExecutionResult, require_row_value
from src.application.infrastructure.neo4j.repository.statement import CypherStatement, CypherStatementTemplate


_ADDRESS_BY_ID_STATEMENT_TEMPLATE = CypherStatementTemplate(
    name="address.find_by_id",
    cypher="""
MATCH (address:Address {id: $address_id})
RETURN
    address.id AS address_id,
    address.house_number AS house_number,
    address.latitude AS latitude,
    address.longitude AS longitude
""".strip(),
)


class AddressByIdCypherStatementBuilder(CypherStatementBuilder[FindAddressByIdQuery]):
    """Builds the Cypher statement for reading a single address by identifier."""

    def build(self, request_model: FindAddressByIdQuery) -> CypherStatement:
        return _ADDRESS_BY_ID_STATEMENT_TEMPLATE.bind({"address_id": request_model.address_id.value})


class AddressByIdResultProjector(Neo4jResultProjector[Address | None]):
    """Projects a Neo4j execution result into an address domain model."""

    def project(self, execution_result: Neo4jExecutionResult) -> Address | None:
        return _ADDRESS_RESULT_HANDLERS.get(
            execution_result.record_count,
            _raise_ambiguous_address_result,
        )(execution_result)


class Neo4jAddressByIdRepository(
    Neo4jReadRepositoryAdapter[FindAddressByIdQuery, Address | None],
    AddressByIdRepositoryPort,
):
    """Concrete address repository built on the shared Neo4j read adapter base."""

    def __init__(self, repository_executor: Neo4jRepositoryExecutorProtocol) -> None:
        super().__init__(
            repository_name=self.__class__.__name__,
            operation_name="get_by_id",
            statement_builder=AddressByIdCypherStatementBuilder(),
            result_projector=AddressByIdResultProjector(),
            repository_executor=repository_executor,
        )


def _return_no_address(execution_result: Neo4jExecutionResult) -> Address | None:
    del execution_result
    return None


def _map_single_address(execution_result: Neo4jExecutionResult) -> Address:
    record = execution_result.records[0]
    return Address(
        id=NodeId(
            str(
                require_row_value(
                    statement_name=execution_result.statement_name,
                    row=record,
                    field_name="address_id",
                )
            )
        ),
        house_number=str(
            require_row_value(
                statement_name=execution_result.statement_name,
                row=record,
                field_name="house_number",
            )
        ),
        geo_location=_create_geo_location(record.get("latitude"), record.get("longitude")),
    )


def _raise_ambiguous_address_result(execution_result: Neo4jExecutionResult) -> Address | None:
    raise ValueError(
        f"Statement '{execution_result.statement_name}' expected at most one address record "
        f"but received {execution_result.record_count}"
    )


def _create_geo_location(latitude: object, longitude: object) -> GeoLocation | None:
    geo_location_factories = {
        (True, True): _return_no_geo_location,
        (False, False): _return_complete_geo_location,
    }
    return geo_location_factories.get(
        (latitude is None, longitude is None),
        _raise_incomplete_geo_location,
    )(latitude, longitude)


def _return_no_geo_location(latitude: object, longitude: object) -> GeoLocation | None:
    del latitude, longitude
    return None


def _return_complete_geo_location(latitude: object, longitude: object) -> GeoLocation:
    return GeoLocation(latitude=float(latitude), longitude=float(longitude))


def _raise_incomplete_geo_location(latitude: object, longitude: object) -> GeoLocation | None:
    raise ValueError(
        "Address geo location must provide both latitude and longitude or neither "
        f"(latitude={latitude!r}, longitude={longitude!r})"
    )


_ADDRESS_RESULT_HANDLERS = {
    0: _return_no_address,
    1: _map_single_address,
}
