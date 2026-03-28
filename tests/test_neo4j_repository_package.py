"""Tests for lightweight Neo4j repository package imports and registry validation."""

import builtins
import importlib
import sys
import unittest
from unittest.mock import patch

from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
from src.application.infrastructure.neo4j.repository.error import Neo4jRepositoryConfigurationError
from src.application.infrastructure.neo4j.repository.registry import Neo4jAccessModeRegistry


class Neo4jRepositoryPackageTest(unittest.TestCase):
    def test_repository_imports_stay_lightweight_when_neo4j_imports_are_blocked(self) -> None:
        guarded_modules = (
            "src.application.infrastructure.neo4j.repository",
            "src.application.infrastructure.neo4j.repository.executor",
            "src.application.infrastructure.neo4j.repository.driver_integration",
            "src.application.infrastructure.neo4j.session_provider",
            "src.application.infrastructure.neo4j.connection_factory",
        )
        for module_name in guarded_modules:
            sys.modules.pop(module_name, None)

        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith("neo4j"):
                raise AssertionError("neo4j import should not happen during lightweight module import")
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=guarded_import):
            repository_package = importlib.import_module("src.application.infrastructure.neo4j.repository")
            executor_module = importlib.import_module("src.application.infrastructure.neo4j.repository.executor")
            session_provider_module = importlib.import_module("src.application.infrastructure.neo4j.session_provider")
            connection_factory_module = importlib.import_module("src.application.infrastructure.neo4j.connection_factory")

        self.assertEqual("CypherStatement", repository_package.CypherStatement.__name__)
        self.assertEqual("Neo4jRepositoryExecutor", executor_module.Neo4jRepositoryExecutor.__name__)
        self.assertEqual("Neo4jSessionProvider", session_provider_module.Neo4jSessionProvider.__name__)
        self.assertEqual("Neo4jConnectionFactory", connection_factory_module.Neo4jConnectionFactory.__name__)

    def test_access_mode_registry_rejects_missing_modes(self) -> None:
        with self.assertRaises(Neo4jRepositoryConfigurationError) as raised_error:
            Neo4jAccessModeRegistry(
                registry_name="transaction strategies",
                entries={Neo4jAccessMode.READ: object()},
            )

        self.assertIn("missing entries for access modes: write", str(raised_error.exception))

    def test_access_mode_registry_rejects_unknown_lookup_modes(self) -> None:
        registry = Neo4jAccessModeRegistry(
            registry_name="transaction strategies",
            entries={
                Neo4jAccessMode.READ: object(),
                Neo4jAccessMode.WRITE: object(),
            },
        )

        with self.assertRaises(Neo4jRepositoryConfigurationError) as raised_error:
            registry.get("read")  # type: ignore[arg-type]

        self.assertIn("unsupported access mode", str(raised_error.exception))


if __name__ == "__main__":
    unittest.main()
