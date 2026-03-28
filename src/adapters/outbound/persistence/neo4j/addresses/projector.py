"""Result projectors for address read operations."""

from src.adapters.outbound.persistence.neo4j.addresses.mapper import Neo4jAddressRecordMapper
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jResultProjector
from src.adapters.outbound.persistence.neo4j.repository.result import Neo4jExecutionResult
from src.domain.addresses.model.address import Address


class SingleAddressProjector(Neo4jResultProjector[Address | None]):
    """Projects an execution result to an optional single address."""

    def __init__(self, record_mapper: Neo4jAddressRecordMapper | None = None) -> None:
        self._record_mapper = record_mapper or Neo4jAddressRecordMapper()

    def project(self, execution_result: Neo4jExecutionResult) -> Address | None:
        return _SINGLE_RESULT_HANDLERS.get(
            execution_result.record_count,
            _raise_ambiguous_address_result,
        )(execution_result, self._record_mapper)


class AddressCollectionProjector(Neo4jResultProjector[tuple[Address, ...]]):
    """Projects an execution result to a stable tuple of addresses."""

    def __init__(self, record_mapper: Neo4jAddressRecordMapper | None = None) -> None:
        self._record_mapper = record_mapper or Neo4jAddressRecordMapper()

    def project(self, execution_result: Neo4jExecutionResult) -> tuple[Address, ...]:
        return self._record_mapper.map_all(
            statement_name=execution_result.statement_name,
            rows=execution_result.records,
        )


def _return_no_address(
    execution_result: Neo4jExecutionResult,
    record_mapper: Neo4jAddressRecordMapper,
) -> Address | None:
    del execution_result, record_mapper
    return None


def _map_single_address(
    execution_result: Neo4jExecutionResult,
    record_mapper: Neo4jAddressRecordMapper,
) -> Address:
    return record_mapper.map_one(
        statement_name=execution_result.statement_name,
        row=execution_result.records[0],
    )


def _raise_ambiguous_address_result(
    execution_result: Neo4jExecutionResult,
    record_mapper: Neo4jAddressRecordMapper,
) -> Address | None:
    del record_mapper
    raise ValueError(
        f"Statement '{execution_result.statement_name}' expected at most one address record "
        f"but received {execution_result.record_count}"
    )


_SINGLE_RESULT_HANDLERS = {
    0: _return_no_address,
    1: _map_single_address,
}
