"""Unit tests for Neo4j driver connection configuration."""

import unittest
from unittest.mock import MagicMock, patch

from src.infrastructure.neo4j.config import Neo4jConfig
from src.infrastructure.neo4j.connection_factory import Neo4jConnectionFactory


class Neo4jConnectionFactoryTest(unittest.TestCase):
    def test_create_driver_passes_notification_filters(self) -> None:
        config = Neo4jConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            notifications_min_severity="OFF",
            warn_notification_severity="OFF",
        )
        driver = MagicMock()

        with patch("neo4j.GraphDatabase.driver", return_value=driver) as driver_factory:
            result = Neo4jConnectionFactory(config).create_driver()

        driver_factory.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("neo4j", "password"),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=30,
            notifications_min_severity="OFF",
            warn_notification_severity="OFF",
        )
        driver.verify_connectivity.assert_called_once_with()
        self.assertIs(driver, result)


if __name__ == "__main__":
    unittest.main()
