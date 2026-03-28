import os
from dataclasses import dataclass

from src.infrastructure.validation import require_non_blank, require_positive_integer


@dataclass(frozen=True, slots=True)
class Neo4jConfig:
    uri: str
    username: str
    password: str
    database: str = "neo4j"
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 50
    connection_acquisition_timeout: int = 30

    def __post_init__(self) -> None:
        """Validate connection settings before they are consumed by infrastructure adapters."""
        object.__setattr__(
            self,
            "uri",
            require_non_blank(owner=self.__class__.__name__, field_name="uri", value=self.uri),
        )
        object.__setattr__(
            self,
            "username",
            require_non_blank(owner=self.__class__.__name__, field_name="username", value=self.username),
        )
        object.__setattr__(
            self,
            "password",
            require_non_blank(owner=self.__class__.__name__, field_name="password", value=self.password),
        )
        object.__setattr__(
            self,
            "database",
            require_non_blank(owner=self.__class__.__name__, field_name="database", value=self.database),
        )
        require_positive_integer(
            owner=self.__class__.__name__,
            field_name="max_connection_lifetime",
            value=self.max_connection_lifetime,
        )
        require_positive_integer(
            owner=self.__class__.__name__,
            field_name="max_connection_pool_size",
            value=self.max_connection_pool_size,
        )
        require_positive_integer(
            owner=self.__class__.__name__,
            field_name="connection_acquisition_timeout",
            value=self.connection_acquisition_timeout,
        )

    @staticmethod
    def from_env() -> "Neo4jConfig":
        return Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "MeinSicheresPasswort123"),
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
            max_connection_lifetime=int(os.getenv("NEO4J_MAX_CONNECTION_LIFETIME", "3600")),
            max_connection_pool_size=int(os.getenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "50")),
            connection_acquisition_timeout=int(os.getenv("NEO4J_CONNECTION_ACQUISITION_TIMEOUT", "30")),
        )



