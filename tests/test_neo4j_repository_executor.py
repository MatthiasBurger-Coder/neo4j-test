"""Unit tests for the Neo4j repository executor foundation."""

from dataclasses import dataclass
import unittest

from src.infrastructure.context.correlation_id import CorrelationIdContext
from src.adapters.outbound.persistence.neo4j.repository.access_mode import Neo4jAccessMode
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jResultProjector
from src.adapters.outbound.persistence.neo4j.repository.error import (
    Neo4jReadRepositoryError,
    Neo4jWriteRepositoryError,
)
from src.adapters.outbound.persistence.neo4j.repository.executor import Neo4jRepositoryExecutor
from src.adapters.outbound.persistence.neo4j.repository.operation import Neo4jRepositoryOperationContextFactory
from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement, CypherStatementTemplate


@dataclass(frozen=True, slots=True)
class _FakeCounters:
    nodes_created: int = 0
    nodes_deleted: int = 0
    relationships_created: int = 0
    relationships_deleted: int = 0
    properties_set: int = 0
    labels_added: int = 0
    labels_removed: int = 0
    indexes_added: int = 0
    indexes_removed: int = 0
    constraints_added: int = 0
    constraints_removed: int = 0
    contains_updates: bool = False
    contains_system_updates: bool = False


@dataclass(frozen=True, slots=True)
class _FakeSummary:
    counters: _FakeCounters = _FakeCounters()
    query_type: str = "r"
    database: str = "neo4j"


class _FakeQuery:
    def __init__(self, text: str, metadata: dict[str, object]) -> None:
        self.text = text
        self.metadata = metadata


class _FakeQueryFactory:
    def create(self, *, cypher: str, metadata: dict[str, object]) -> _FakeQuery:
        return _FakeQuery(text=cypher, metadata=dict(metadata))


class _OSErrorFailureClassifier:
    def is_execution_failure(self, error: BaseException) -> bool:
        return isinstance(error, OSError)


class _FakeRecord:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def data(self) -> dict[str, object]:
        return dict(self._payload)


class _FakeQueryResult:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self._records = [_FakeRecord(record) for record in records]

    def keys(self) -> list[str]:
        return list(self._records[0].data().keys()) if self._records else []

    def __iter__(self):
        return iter(self._records)

    def consume(self) -> _FakeSummary:
        return _FakeSummary()


class _FakeTransaction:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self._records = records
        self.last_query = None
        self.last_parameters = None

    def run(self, query, parameters):
        self.last_query = query
        self.last_parameters = parameters
        return _FakeQueryResult(self._records)


class _OSErrorTransaction:
    def run(self, query, parameters):
        del query, parameters
        raise OSError("database unavailable")


class _ValueErrorTransaction:
    def run(self, query, parameters):
        del query, parameters
        raise ValueError("unexpected mapper failure")


class _FakeSession:
    def __init__(self, transaction) -> None:
        self._transaction = transaction

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def execute_read(self, work):
        return work(self._transaction)

    def execute_write(self, work):
        return work(self._transaction)


class _FakeSessionProvider:
    def __init__(self, session: _FakeSession) -> None:
        self._session = session
        self.database = "neo4j"
        self.last_mode = None

    def open_session(self, access_mode: Neo4jAccessMode):
        self.last_mode = access_mode
        return self._session


class _DictionaryProjector(Neo4jResultProjector[list[dict[str, object]]]):
    def project(self, execution_result):
        return [dict(row) for row in execution_result.records]


class _ExplodingProjector(Neo4jResultProjector[object]):
    def project(self, execution_result):
        del execution_result
        raise ValueError("projection failed")


class Neo4jRepositoryExecutorTest(unittest.TestCase):
    def tearDown(self) -> None:
        CorrelationIdContext.clear()

    def test_execute_read_projects_records_and_propagates_correlation_id(self) -> None:
        CorrelationIdContext.set("corr-read-123")
        transaction = _FakeTransaction(records=[{"person_id": "p-1"}])
        session = _FakeSession(transaction)
        session_provider = _FakeSessionProvider(session)
        executor = Neo4jRepositoryExecutor(
            session_provider,
            context_factory=Neo4jRepositoryOperationContextFactory(
                database_name=session_provider.database,
                correlation_id_supplier=CorrelationIdContext.get,
            ),
            query_factory=_FakeQueryFactory(),
            failure_classifier=_OSErrorFailureClassifier(),
        )

        result = executor.execute_read(
            repository_name="PersonReadRepository",
            operation_name="execute",
            statement=CypherStatementTemplate(
                name="person.find_by_id",
                cypher="MATCH (p:Person {id: $person_id}) RETURN p.id AS person_id",
            ).bind({"person_id": "p-1"}),
            result_projector=_DictionaryProjector(),
        )

        self.assertEqual([{"person_id": "p-1"}], result)
        self.assertEqual(Neo4jAccessMode.READ, session_provider.last_mode)
        self.assertEqual("corr-read-123", transaction.last_query.metadata["correlation_id"])
        self.assertEqual("person.find_by_id", transaction.last_query.metadata["statement_name"])

    def test_execute_write_translates_execution_failures(self) -> None:
        session_provider = _FakeSessionProvider(_FakeSession(_OSErrorTransaction()))
        executor = Neo4jRepositoryExecutor(
            session_provider,
            context_factory=Neo4jRepositoryOperationContextFactory(
                database_name=session_provider.database,
                correlation_id_supplier=CorrelationIdContext.get,
            ),
            query_factory=_FakeQueryFactory(),
            failure_classifier=_OSErrorFailureClassifier(),
        )

        with self.assertRaises(Neo4jWriteRepositoryError) as raised_error:
            executor.execute_write(
                repository_name="PersonWriteRepository",
                operation_name="execute",
                statement=CypherStatement(
                    name="person.save",
                    cypher="CREATE (p:Person {id: $person_id})",
                    parameters={"person_id": "p-1"},
                ),
                result_projector=_DictionaryProjector(),
            )

        self.assertIn("stage=execution", str(raised_error.exception))
        self.assertIn("statement=person.save", str(raised_error.exception))
        self.assertIn("technical_error=OSError: database unavailable", str(raised_error.exception))

    def test_execute_read_translates_projection_failures(self) -> None:
        transaction = _FakeTransaction(records=[{"person_id": "p-1"}])
        session_provider = _FakeSessionProvider(_FakeSession(transaction))
        executor = Neo4jRepositoryExecutor(
            session_provider,
            context_factory=Neo4jRepositoryOperationContextFactory(
                database_name=session_provider.database,
                correlation_id_supplier=CorrelationIdContext.get,
            ),
            query_factory=_FakeQueryFactory(),
            failure_classifier=_OSErrorFailureClassifier(),
        )

        with self.assertRaises(Neo4jReadRepositoryError) as raised_error:
            executor.execute_read(
                repository_name="PersonReadRepository",
                operation_name="execute",
                statement=CypherStatement(
                    name="person.find_by_id",
                    cypher="MATCH (p:Person {id: $person_id}) RETURN p.id AS person_id",
                    parameters={"person_id": "p-1"},
                ),
                result_projector=_ExplodingProjector(),
            )

        self.assertIn("stage=projection", str(raised_error.exception))
        self.assertIn("technical_error=ValueError: projection failed", str(raised_error.exception))

    def test_execute_read_keeps_unclassified_execution_errors_visible(self) -> None:
        session_provider = _FakeSessionProvider(_FakeSession(_ValueErrorTransaction()))
        executor = Neo4jRepositoryExecutor(
            session_provider,
            context_factory=Neo4jRepositoryOperationContextFactory(
                database_name=session_provider.database,
                correlation_id_supplier=CorrelationIdContext.get,
            ),
            query_factory=_FakeQueryFactory(),
            failure_classifier=_OSErrorFailureClassifier(),
        )

        with self.assertRaises(ValueError) as raised_error:
            executor.execute_read(
                repository_name="PersonReadRepository",
                operation_name="execute",
                statement=CypherStatement(
                    name="person.find_by_id",
                    cypher="MATCH (p:Person {id: $person_id}) RETURN p.id AS person_id",
                    parameters={"person_id": "p-1"},
                ),
                result_projector=_DictionaryProjector(),
            )

        self.assertEqual("unexpected mapper failure", str(raised_error.exception))


if __name__ == "__main__":
    unittest.main()



