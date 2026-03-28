"""Result projectors for address write operations."""

from src.adapters.outbound.persistence.neo4j.addresses.mapper import Neo4jAddressRecordMapper
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jResultProjector
from src.adapters.outbound.persistence.neo4j.repository.result import Neo4jExecutionResult
from src.domain.addresses.model.address import Address


class CreatedAddressProjector(Neo4jResultProjector[Address]):
    """Projects an execution result to the created address domain object."""

    def __init__(self, record_mapper: Neo4jAddressRecordMapper | None = None) -> None:
        self._record_mapper = record_mapper or Neo4jAddressRecordMapper()

    def project(self, execution_result: Neo4jExecutionResult) -> Address:
        return _CREATE_RESULT_HANDLERS.get(
            execution_result.record_count,
            _raise_invalid_create_result,
        )(execution_result, self._record_mapper)


def _map_created_address(
    execution_result: Neo4jExecutionResult,
    record_mapper: Neo4jAddressRecordMapper,
) -> Address:
    return record_mapper.map_one(
        statement_name=execution_result.statement_name,
        row=execution_result.records[0],
    )


def _raise_invalid_create_result(
    execution_result: Neo4jExecutionResult,
    record_mapper: Neo4jAddressRecordMapper,
) -> Address:
    del record_mapper
    raise ValueError(
        f"Statement '{execution_result.statement_name}' expected exactly one created address record "
        f"but received {execution_result.record_count}"
    )


_CREATE_RESULT_HANDLERS = {
    1: _map_created_address,
}
