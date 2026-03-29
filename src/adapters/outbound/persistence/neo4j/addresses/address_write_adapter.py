"""Neo4j write adapter for the address domain."""

from src.adapters.outbound.persistence.neo4j.addresses.write_mapper import (
    AddressContextToCreateAddressContextWriteModelMapper,
)
from src.adapters.outbound.persistence.neo4j.addresses.write_model import (
    CreateAddressContextWriteModel,
)
from src.adapters.outbound.persistence.neo4j.addresses.write_projector import (
    CreatedAddressContextProjector,
)
from src.adapters.outbound.persistence.neo4j.addresses.write_queries import (
    CreateAddressContextStatementBuilder,
)
from src.adapters.outbound.persistence.neo4j.repository.adapter import Neo4jWriteRepositoryAdapter
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jRepositoryExecutorProtocol
from src.adapters.outbound.persistence.neo4j.repository.error import Neo4jWriteRepositoryError
from src.application.addresses.address_context import AddressContextDraft, CreatedAddressContext
from src.application.addresses.address_write_port import AddressWriteError, AddressWritePort


_ADDRESS_WRITE_REPOSITORY_NAME = "Neo4jAddressWriteAdapter"


class Neo4jAddressWriteAdapter(AddressWritePort):
    """Implements address-context write operations through Neo4j-backed repositories."""

    def __init__(self, repository_executor: Neo4jRepositoryExecutorProtocol) -> None:
        self._write_model_mapper = AddressContextToCreateAddressContextWriteModelMapper()
        self._create_address_repository = _CreateAddressRepository(
            repository_executor=repository_executor,
            statement_builder=CreateAddressContextStatementBuilder(),
        )

    def create_address(self, address_context: AddressContextDraft) -> CreatedAddressContext:
        try:
            return self._create_address_repository.execute(self._write_model_mapper.map(address_context))
        except Neo4jWriteRepositoryError as error:
            raise AddressWriteError("Address context persistence failed") from error


class _CreateAddressRepository(
    Neo4jWriteRepositoryAdapter[CreateAddressContextWriteModel, CreatedAddressContext]
):
    """Internal write operation for persisting one address context."""

    def __init__(
        self,
        *,
        repository_executor: Neo4jRepositoryExecutorProtocol,
        statement_builder: CreateAddressContextStatementBuilder,
    ) -> None:
        super().__init__(
            repository_name=_ADDRESS_WRITE_REPOSITORY_NAME,
            operation_name="create_address",
            statement_builder=statement_builder,
            result_projector=CreatedAddressContextProjector(),
            repository_executor=repository_executor,
        )
