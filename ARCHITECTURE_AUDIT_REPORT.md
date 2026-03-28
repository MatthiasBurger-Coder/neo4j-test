# Architektur-Audit-Bericht

## 1. Kurzfassung

Die Codebasis wurde repository-weit gegen `AGENTS.md` geprüft und in eine klarere hexagonale Struktur überführt. Die größten Verstöße lagen in einer semantisch falschen Schichtung unter `src/application/...`, falsch platzierten Neo4j-Adaptern, verstreuten technischen Hilfen und Adapter-Abhängigkeiten auf Infrastrukturmodule. Diese Punkte wurden automatisch bereinigt, ohne das beobachtbare Laufzeitverhalten der vorhandenen Tests zu verändern.

## 2. Zielbild laut AGENTS.md

Das Zielbild aus `AGENTS.md` verlangt:

- reine Domäne ohne Infrastruktur-, Datenbank-, Logging- oder Adapterabhängigkeiten
- Ports auf der Core-Seite
- konkrete Neo4j-Repositorys als sekundäre Adapter
- Infrastruktur für Logging, Context, Konfiguration, Driver-/Session-Handling und Bootstrap
- einen einzigen Composition Root
- bevorzugt kleine, explizite Bausteine statt schwergewichtiger Mischmodule

Die bereinigte Struktur lautet jetzt fachlich:

```text
src/
  domain/
  adapters/
    outbound/
      persistence/
        neo4j/
  infrastructure/
    bootstrap/
    context/
    logging/
    neo4j/
```

## 3. Gefundene Verstöße

### A. Layer-Verstöße

- `src/application/domain/...`
  - Verstoß: Domain-Code lag im `application`-Teilbaum.
  - Problem: Die Schichtgrenze war semantisch falsch und erschwerte die Hexagon-Zuordnung.
  - Zielbild: `src/domain/...`

- `src/application/infrastructure/neo4j/...`
  - Verstoß: Konkrete Neo4j-Repositorys und Repository-Basis lagen unter `application.infrastructure`.
  - Problem: Sekundäre Adapter waren nicht als Adapter modelliert.
  - Zielbild: `src/adapters/outbound/persistence/neo4j/...`

- `src/application/port/outbound/repository/...`
  - Verstoß: Generische Repository-Ports lagen im Application-Paket, obwohl Domain-Ports davon abhingen.
  - Problem: Domain -> Application-Abhängigkeit.
  - Zielbild: `src/domain/ports/repository/...`

- `src/bootstrap/...`
  - Verstoß: Composition Root lag außerhalb der Infrastruktur-Schicht.
  - Problem: Infrastruktur-Wiring war nicht dort verortet, wo `AGENTS.md` es fordert.
  - Zielbild: `src/infrastructure/bootstrap/...`

### B. Persistenz-/Neo4j-Verstöße

- `src/application/infrastructure/neo4j/addresses/address_by_id_repository.py`
  - Verstoß: konkreter sekundärer Adapter im falschen Layer.
  - Zielbild: `src/adapters/outbound/persistence/neo4j/addresses/...`

- `src/application/infrastructure/neo4j/repository/...`
  - Verstoß: technische Repository-Basis war nicht als Adapterpaket verortet.
  - Zielbild: `src/adapters/outbound/persistence/neo4j/repository/...`

### C. Logging-/Technik-Kopplungsverstöße

- Adapter-Module importierten Infrastruktur-Module direkt:
  - vorher u. a. `repository/adapter.py`, `error.py`, `operation.py`, `registry.py`, `statement.py`, `executor.py`
  - Verstoß: Adapter -> Infrastruktur-Kopplung
  - Zielbild: pure Domain-Helfer oder Injektion aus der Infrastruktur

### D. Control-Flow-/Strukturverstöße

- Mehrfach duplizierte Non-Blank-Validierung in Domain-Objekten
  - Verstoß: wiederholte technische Kleinstlogik ohne gemeinsamen Zuschnitt
  - Zielbild: kleine zentrale Validierungsbausteine in Domain und Infrastruktur

### E. Test-/Pfadverstöße

- Tests referenzierten die alte, falsche Schichtstruktur
  - Verstoß: Testpfade spiegelten die Architekturverletzung
  - Zielbild: Tests referenzieren die bereinigten Layer

## 4. Automatisch korrigierte Verstöße

- Domain von `src/application/domain/...` nach `src/domain/...` verschoben
- Domain-Ports nach `src/domain/addresses/ports/...` verschoben
- generische Repository-Ports nach `src/domain/ports/repository/...` verschoben
- Neo4j-Adapter nach `src/adapters/outbound/persistence/neo4j/...` verschoben
- Logging, Context, Neo4j-Konfiguration, Driver-/Session-Handling nach `src/infrastructure/...` verschoben
- Composition Root nach `src/infrastructure/bootstrap/...` verschoben
- `src/app.py` auf den neuen Composition Root umgestellt
- Importpfade im gesamten Repository aktualisiert
- Adapter von Infrastruktur entkoppelt:
  - keine Adapter-Imports von `src.infrastructure.logging`
  - keine Adapter-Imports von `src.infrastructure.context`
  - keine Adapter-Imports von `src.infrastructure.validation`
- CorrelationId-Zugriff aus dem Neo4j-Adapter entfernt und sauber im Bootstrap injiziert
- Logger-Zugriff im Neo4j-Executor von Infrastruktur-Fabrik entkoppelt; zentrale Logging-Konfiguration bleibt trotzdem maßgeblich
- gemeinsame Domain-Validierung in `src/domain/shared/validation.py` eingeführt
- gemeinsame Infrastruktur-Validierung in `src/infrastructure/validation.py` erweitert
- Domain-Modelle auf die gemeinsamen Validierungen umgestellt
- Tests auf die neue Architektur umgestellt
- semantisch falsche Altmodule unter `src/application/...` gelöscht

## 5. Nicht vollständig automatisch korrigierbare Punkte

- Es existiert aktuell keine ausgebaute Application-Schicht mit Use Cases oder Application Services.
  - Das ist im aktuellen Zuschnitt kein akuter Regelverstoß, aber die Architektur ist hier noch minimal.
  - Für künftige fachliche Orchestrierung sollten neue Use Cases direkt unter `src/application/...` entstehen.

- Lokale, unversionierte Leerordner bzw. Cache-Verzeichnisse aus der alten Struktur koennen im Arbeitsverzeichnis weiter vorhanden sein.
  - Diese sind kein Teil des Repository-Inhalts.
  - Der versionierte Codezustand ist bereinigt.

## 6. Konkrete verbleibende Risiken oder Tradeoffs

- `src/infrastructure/neo4j/session_provider.py` verwendet weiterhin technische Repository-Typen aus dem Neo4j-Adapter-Baustein.
  - Das ist nach `AGENTS.md` zulaessig, weil Infrastruktur nach innen auf Adapter/Core zeigen darf.
  - Der Zuschnitt ist technisch kohärent, weil die Access-Mode-Semantik spezifisch fuer den Neo4j-Repository-Baustein ist.

- Die Anwendung ist weiterhin sehr klein.
  - Dadurch ist die Trennung jetzt sauber, aber noch nicht durch echte Use-Case-Module demonstriert.

## 7. Durchgeführte Verifikationsschritte

- `python -m pytest -q`
- `python -m unittest discover -s tests`
- `python -m compileall src tests`

Ergebnis:

- `12 passed in 0.13s`
- `unittest`: `Ran 12 tests ... OK`
- `compileall` erfolgreich

Ein dedizierter Linter ist im Repository derzeit nicht konfiguriert. `compileall` traversiert dabei weiterhin lokale Leerordner der alten Struktur, aber keine verbliebenen Altmodule.

## 8. Ergebnisstatus

Status: **erfolgreich bereinigt**

Die Repository-Struktur ist jetzt deutlich näher am Zielbild aus `AGENTS.md`:

- Domäne ist rein und sauber getrennt
- Neo4j-Repositorys sind sekundäre Adapter
- Infrastruktur kapselt Logging, Context, Driver, Session und Bootstrap
- Composition Root ist zentralisiert
- Tests folgen der bereinigten Architektur
- die Codebasis ist testbarer und schichttreuer als vor dem Audit
