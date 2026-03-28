"""Neo4j write adapter for the address domain."""

from src.adapters.outbound.persistence.neo4j.addresses.write_mapper import (
    AddressToCreateAddressWriteModelMapper,
)
from src.adapters.outbound.persistence.neo4j.addresses.write_model import CreateAddressWriteModel
from src.adapters.outbound.persistence.neo4j.addresses.write_projector import (
    CreatedAddressProjector,
)
from src.adapters.outbound.persistence.neo4j.addresses.write_queries import (
    CreateAddressStatementBuilder,
)
from src.adapters.outbound.persistence.neo4j.repository.adapter import Neo4jWriteRepositoryAdapter
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jRepositoryExecutorProtocol
from src.adapters.outbound.persistence.neo4j.repository.error import Neo4jWriteRepositoryError
from src.application.addresses.address_write_port import AddressWriteError, AddressWritePort
from src.domain.addresses.model.address import Address


_ADDRESS_WRITE_REPOSITORY_NAME = "Neo4jAddressWriteAdapter"


class Neo4jAddressWriteAdapter(AddressWritePort):
    """Implements address write operations through Neo4j-backed repositories."""

    def __init__(self, repository_executor: Neo4jRepositoryExecutorProtocol) -> None:
        self._write_model_mapper = AddressToCreateAddressWriteModelMapper()
        self._create_address_repository = _CreateAddressRepository(
            repository_executor=repository_executor,
            statement_builder=CreateAddressStatementBuilder(),
        )

    def create_address(self, address: Address) -> Address:
        try:
            return self._create_address_repository.execute(self._write_model_mapper.map(address))
        except Neo4jWriteRepositoryError as error:
            raise AddressWriteError("Address persistence failed") from error


class _CreateAddressRepository(Neo4jWriteRepositoryAdapter[CreateAddressWriteModel, Address]):
    """Internal write operation for persisting a single address."""

    def __init__(
        self,
        *,
        repository_executor: Neo4jRepositoryExecutorProtocol,
        statement_builder: CreateAddressStatementBuilder,
    ) -> None:
        super().__init__(
            repository_name=_ADDRESS_WRITE_REPOSITORY_NAME,
            operation_name="create_address",
            statement_builder=statement_builder,
            result_projector=CreatedAddressProjector(),
            repository_executor=repository_executor,
        )
