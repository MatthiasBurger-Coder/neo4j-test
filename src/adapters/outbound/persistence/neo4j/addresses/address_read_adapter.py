"""Neo4j read adapter for the address domain."""

from src.adapters.outbound.persistence.neo4j.addresses.projector import (
    AddressCollectionProjector,
    SingleAddressProjector,
)
from src.adapters.outbound.persistence.neo4j.addresses.queries import (
    FindAddressesByCriteriaStatementBuilder,
)
from src.adapters.outbound.persistence.neo4j.repository.adapter import Neo4jReadRepositoryAdapter
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jRepositoryExecutorProtocol
from src.domain.addresses.model.address import Address
from src.domain.addresses.ports.address_read_repository import (
    AddressReadCriteria,
    AddressReadRepositoryPort,
)
from src.domain.shared.graph.model.node_id import NodeId


_ADDRESS_READ_REPOSITORY_NAME = "Neo4jAddressReadAdapter"


class Neo4jAddressReadAdapter(AddressReadRepositoryPort):
    """Implements address read operations through Neo4j-backed read repositories."""

    def __init__(self, repository_executor: Neo4jRepositoryExecutorProtocol) -> None:
        statement_builder = FindAddressesByCriteriaStatementBuilder()
        self._find_by_id_repository = _FindAddressByIdRepository(
            repository_executor=repository_executor,
            statement_builder=statement_builder,
        )
        self._find_all_repository = _FindAllAddressesRepository(
            repository_executor=repository_executor,
            statement_builder=statement_builder,
        )
        self._find_by_criteria_repository = _FindAddressesByCriteriaRepository(
            repository_executor=repository_executor,
            statement_builder=statement_builder,
        )

    def find_by_id(self, address_id: NodeId) -> Address | None:
        return self._find_by_id_repository.execute(
            AddressReadCriteria(address_ids=(address_id,))
        )

    def find_all(self) -> tuple[Address, ...]:
        return self._find_all_repository.execute(AddressReadCriteria())

    def find_by_criteria(self, criteria: AddressReadCriteria) -> tuple[Address, ...]:
        return self._find_by_criteria_repository.execute(criteria)


class _FindAddressByIdRepository(Neo4jReadRepositoryAdapter[AddressReadCriteria, Address | None]):
    """Internal read operation for loading a single address by id."""

    def __init__(
        self,
        *,
        repository_executor: Neo4jRepositoryExecutorProtocol,
        statement_builder: FindAddressesByCriteriaStatementBuilder,
    ) -> None:
        super().__init__(
            repository_name=_ADDRESS_READ_REPOSITORY_NAME,
            operation_name="find_by_id",
            statement_builder=statement_builder,
            result_projector=SingleAddressProjector(),
            repository_executor=repository_executor,
        )


class _FindAddressesByCriteriaRepository(
    Neo4jReadRepositoryAdapter[AddressReadCriteria, tuple[Address, ...]]
):
    """Internal read operation for loading address collections."""

    def __init__(
        self,
        *,
        repository_executor: Neo4jRepositoryExecutorProtocol,
        statement_builder: FindAddressesByCriteriaStatementBuilder,
    ) -> None:
        super().__init__(
            repository_name=_ADDRESS_READ_REPOSITORY_NAME,
            operation_name="find_by_criteria",
            statement_builder=statement_builder,
            result_projector=AddressCollectionProjector(),
            repository_executor=repository_executor,
        )


class _FindAllAddressesRepository(
    Neo4jReadRepositoryAdapter[AddressReadCriteria, tuple[Address, ...]]
):
    """Internal read operation for loading all addresses."""

    def __init__(
        self,
        *,
        repository_executor: Neo4jRepositoryExecutorProtocol,
        statement_builder: FindAddressesByCriteriaStatementBuilder,
    ) -> None:
        super().__init__(
            repository_name=_ADDRESS_READ_REPOSITORY_NAME,
            operation_name="find_all",
            statement_builder=statement_builder,
            result_projector=AddressCollectionProjector(),
            repository_executor=repository_executor,
        )
