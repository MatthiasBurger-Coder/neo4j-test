"""Tests for lightweight Neo4j repository package imports and registry validation."""

import importlib
import sys
import unittest

from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
from src.application.infrastructure.neo4j.repository.error import Neo4jRepositoryConfigurationError
from src.application.infrastructure.neo4j.repository.registry import Neo4jAccessModeRegistry


class Neo4jRepositoryPackageTest(unittest.TestCase):
    def test_package_import_stays_lightweight_until_specific_exports_are_requested(self) -> None:
        sys.modules.pop("src.application.infrastructure.neo4j.repository", None)
        sys.modules.pop("src.application.infrastructure.neo4j.repository.executor", None)

        repository_package = importlib.import_module("src.application.infrastructure.neo4j.repository")

        self.assertNotIn("src.application.infrastructure.neo4j.repository.executor", sys.modules)
        self.assertEqual(
            "CypherStatement",
            repository_package.CypherStatement.__name__,
        )
        self.assertNotIn("src.application.infrastructure.neo4j.repository.executor", sys.modules)

    def test_access_mode_registry_rejects_missing_modes(self) -> None:
        with self.assertRaises(Neo4jRepositoryConfigurationError) as raised_error:
            Neo4jAccessModeRegistry(
                registry_name="transaction strategies",
                entries={Neo4jAccessMode.READ: object()},
            )

        self.assertIn("missing entries for access modes: write", str(raised_error.exception))


if __name__ == "__main__":
    unittest.main()
