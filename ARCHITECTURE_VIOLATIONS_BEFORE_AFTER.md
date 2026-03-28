# Architekturverstöße Vorher/Nachher

| Pfad | Ursprünglicher Verstoß | Korrektur | Endgültige Verantwortung |
| --- | --- | --- | --- |
| `src/application/domain/addresses/model/*.py` -> `src/domain/addresses/model/*.py` | Domain unter `application` falsch verortet | in echte Domain-Schicht verschoben | reine Address-Domain-Modelle |
| `src/application/domain/shared/graph/model/*.py` -> `src/domain/shared/graph/model/*.py` | Shared-Domain-Bausteine unter `application` falsch verortet | in `src/domain/shared/graph/model` verschoben | reine Domain-Grundtypen |
| `src/application/domain/addresses/port/address_by_id_repository.py` -> `src/domain/addresses/ports/address_by_id_repository.py` | Domain-Port in falschem Pfad und mit Domain -> Application-Kopplung | in Domain-Port-Paket verschoben und Imports umgestellt | domain-owned outbound port |
| `src/application/port/outbound/repository/read_repository.py` -> `src/domain/ports/repository/read_repository.py` | generischer Core-Port im Application-Paket | in Domain-Port-Schicht verschoben | generischer Read-Port |
| `src/application/port/outbound/repository/write_repository.py` -> `src/domain/ports/repository/write_repository.py` | generischer Core-Port im Application-Paket | in Domain-Port-Schicht verschoben | generischer Write-Port |
| `src/application/infrastructure/neo4j/addresses/address_by_id_repository.py` -> `src/adapters/outbound/persistence/neo4j/addresses/address_by_id_repository.py` | konkreter Neo4j-Repository-Adapter im Infrastruktur-/Application-Paket | in sekundären Adapter verschoben | Neo4j-Repository-Implementierung |
| `src/application/infrastructure/neo4j/addresses/__init__.py` -> `src/adapters/outbound/persistence/neo4j/addresses/__init__.py` | falsche Schicht für Adapter-Export | in Adapterpaket verschoben | Adapter-Paketexport |
| `src/application/infrastructure/neo4j/repository/__init__.py` -> `src/adapters/outbound/persistence/neo4j/repository/__init__.py` | Repository-Basis nicht als Adapter modelliert | in Adapterpaket verschoben | Neo4j-Repository-Foundation |
| `src/application/infrastructure/neo4j/repository/access_mode.py` -> `src/adapters/outbound/persistence/neo4j/repository/access_mode.py` | technischer Repository-Baustein im falschen Layer | verschoben | technische Access-Mode-Semantik |
| `src/application/infrastructure/neo4j/repository/adapter.py` -> `src/adapters/outbound/persistence/neo4j/repository/adapter.py` | Adapterbasis im falschen Layer und Adapter -> Infrastruktur-Validierung | verschoben und von Infrastruktur entkoppelt | generische Read-/Write-Adapterbasis |
| `src/application/infrastructure/neo4j/repository/contracts.py` -> `src/adapters/outbound/persistence/neo4j/repository/contracts.py` | Adapterinterne Verträge im falschen Layer | verschoben | treiberfreie Adapter-Protokolle |
| `src/application/infrastructure/neo4j/repository/driver_integration.py` -> `src/adapters/outbound/persistence/neo4j/repository/driver_integration.py` | Treiberintegration nicht als Adapterpaket verortet | verschoben | kapselte Neo4j-Treiberintegration |
| `src/application/infrastructure/neo4j/repository/error.py` -> `src/adapters/outbound/persistence/neo4j/repository/error.py` | Adapter-Fehler im falschen Layer und mit Infrastruktur-Validierung gekoppelt | verschoben und entkoppelt | technische Adapterfehler |
| `src/application/infrastructure/neo4j/repository/error_translation.py` -> `src/adapters/outbound/persistence/neo4j/repository/error_translation.py` | Fehlerübersetzer im falschen Layer | verschoben | Strategie-basierte Fehlerübersetzung |
| `src/application/infrastructure/neo4j/repository/executor.py` -> `src/adapters/outbound/persistence/neo4j/repository/executor.py` | Executor im falschen Layer und mit Infrastruktur-Logger/CorrelationId gekoppelt | verschoben, Logger/Context injizierbar gemacht | Neo4j-Repository-Ausführung |
| `src/application/infrastructure/neo4j/repository/operation.py` -> `src/adapters/outbound/persistence/neo4j/repository/operation.py` | Adapter -> Infrastruktur-Kontextkopplung | verschoben und CorrelationId-Supplier injizierbar gemacht | technische Operationskontexte |
| `src/application/infrastructure/neo4j/repository/registry.py` -> `src/adapters/outbound/persistence/neo4j/repository/registry.py` | technischer Registry-Baustein im falschen Layer und an Infrastrukturvalidierung gekoppelt | verschoben und entkoppelt | robuste technische Registry |
| `src/application/infrastructure/neo4j/repository/result.py` -> `src/adapters/outbound/persistence/neo4j/repository/result.py` | Adapter-Resultmodelle im falschen Layer | verschoben | driver-agnostische Resultmodelle |
| `src/application/infrastructure/neo4j/repository/statement.py` -> `src/adapters/outbound/persistence/neo4j/repository/statement.py` | Statement-Baustein im falschen Layer und an Infrastrukturvalidierung gekoppelt | verschoben und entkoppelt | strukturierte Cypher-Statements |
| `src/application/infrastructure/neo4j/repository/strategy.py` -> `src/adapters/outbound/persistence/neo4j/repository/strategy.py` | Strategiebaustein im falschen Layer | verschoben | Transaktionsstrategien |
| `src/application/infrastructure/context/correlation_id.py` -> `src/infrastructure/context/correlation_id.py` | Infrastruktur-Context unter `application` falsch verortet | verschoben | CorrelationId-Context |
| `src/application/infrastructure/context/trace_context.py` -> `src/infrastructure/context/trace_context.py` | Infrastruktur-Context unter `application` falsch verortet | verschoben und auf zentrale Infrastrukturvalidierung umgestellt | Trace-Kontext |
| `src/application/infrastructure/logging/logger_factory.py` -> `src/infrastructure/logging/logger_factory.py` | zentrales Logging im falschen Layerpfad | verschoben | Logger-Erzeugung der Infrastruktur |
| `src/application/infrastructure/logging/logging_config.py` -> `src/infrastructure/logging/logging_config.py` | zentrales Logging im falschen Layerpfad | verschoben | zentrale Logging-Konfiguration |
| `src/application/infrastructure/logging/correlation_id_log_filter.py` -> `src/infrastructure/logging/correlation_id_log_filter.py` | zentrales Logging im falschen Layerpfad | verschoben | CorrelationId-Filter |
| `src/application/infrastructure/neo4j/config.py` -> `src/infrastructure/neo4j/config.py` | Infrastruktur-Konfiguration unter `application` falsch verortet | verschoben | Neo4j-Konfiguration |
| `src/application/infrastructure/neo4j/connection_factory.py` -> `src/infrastructure/neo4j/connection_factory.py` | Driver-Factory im falschen Layerpfad | verschoben | Neo4j-Driver-Erzeugung |
| `src/application/infrastructure/neo4j/session_provider.py` -> `src/infrastructure/neo4j/session_provider.py` | Session-Management im falschen Layerpfad | verschoben | Neo4j-Session-Management |
| `src/application/infrastructure/validation.py` -> `src/infrastructure/validation.py` | technische Infrastrukturvalidierung im falschen Layerpfad | verschoben und erweitert | zentrale Infrastrukturvalidierung |
| `src/bootstrap/application.py` -> `src/infrastructure/bootstrap/application.py` | Composition Root außerhalb der Infrastruktur | verschoben und Context/Logger-Injektion ergänzt | zentraler Bootstrap |
| `src/bootstrap/application_context.py` -> `src/infrastructure/bootstrap/application_context.py` | Bootstrap-Artefakt außerhalb der Infrastruktur | verschoben | bootstrap result object |
| `src/bootstrap/application_repositories.py` -> `src/infrastructure/bootstrap/application_repositories.py` | Bootstrap-Artefakt außerhalb der Infrastruktur | verschoben | zentrales Repository-Wiring |
| `src/bootstrap/application_runtime.py` -> `src/infrastructure/bootstrap/application_runtime.py` | Bootstrap-Artefakt außerhalb der Infrastruktur | verschoben | interne Runtime-Ressourcen |
| `src/app.py` | Entry Point zeigte auf alten Bootstrap-Pfad | Importpfad aktualisiert | minimaler Programmeinstieg |
| `src/domain/shared/validation.py` | wiederholte Domain-Non-Blank-Validierung | neuer gemeinsamer Domain-Helfer eingeführt | kleine pure Domain-Validierung |
| `src/domain/shared/graph/model/node_id.py` | duplizierte Blank-Validierung | auf `src/domain/shared/validation.py` umgestellt | reiner Domain-Value-Object |
| `src/domain/shared/graph/model/relationship_id.py` | duplizierte Blank-Validierung | auf `src/domain/shared/validation.py` umgestellt | reiner Domain-Value-Object |
| `src/domain/addresses/model/address.py` | duplizierte Blank-Validierung | auf `src/domain/shared/validation.py` umgestellt | reines Domain-Modell |
| `src/domain/addresses/model/address_unit.py` | duplizierte Blank-Validierung | auf `src/domain/shared/validation.py` umgestellt | reines Domain-Modell |
| `src/domain/addresses/model/street.py` | duplizierte Blank-Validierung | auf `src/domain/shared/validation.py` umgestellt | reines Domain-Modell |
| `src/domain/addresses/model/building.py` | duplizierte optionale Blank-Validierung | auf `src/domain/shared/validation.py` umgestellt | reines Domain-Modell |
| `src/domain/addresses/model/city.py` | duplizierte Pflicht-/Optional-Validierung | auf `src/domain/shared/validation.py` umgestellt | reines Domain-Modell |
| `src/domain/addresses/model/address_assignment.py` | duplizierte optionale Textvalidierung | auf `src/domain/shared/validation.py` umgestellt | reines Domain-Modell |
| `tests/test_neo4j_address_repository.py` | Tests referenzierten alte Layerpfade | Importe auf neue Schichten umgestellt | Adapter-Unit-Test |
| `tests/test_neo4j_repository_adapter.py` | Tests referenzierten alte Layerpfade | Importe auf neue Schichten umgestellt | Adapter-Unit-Test |
| `tests/test_neo4j_repository_executor.py` | Tests referenzierten alte Layerpfade und implizite Infrastrukturkopplung | Importe umgestellt und ContextFactory explizit injiziert | Executor-Unit-Test |
| `tests/test_neo4j_repository_package.py` | Tests referenzierten alte Layerpfade | Importe und Modulpfade umgestellt | Import-/Registry-Test |
