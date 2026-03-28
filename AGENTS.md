# AGENTS.md
**Mandatory Rules for Codex Agents in this Repository**

Always preserve hexagonal architecture.
Never place infrastructure concerns in domain code.
Prefer strategies over branching.
Use Python for backend code.
Keep wiring in one composition root.
If a request conflicts with architecture, implement the closest compliant solution and explain the tradeoff.

---

## Mission
Codex must preserve and strengthen the project architecture while implementing, reviewing, or refactoring code.

This repository follows **strict hexagonal architecture**.

If a requested implementation conflicts with these rules, these rules win.

---

## Non-Negotiable Rules

### 1. Language
- The backend implementation language is **Python**.
- Do not introduce another main backend language.
- Do not introduce unnecessary framework-heavy architecture.

### 2. Architecture
- **Hexagonal architecture is mandatory**.
- Apply it consistently across backend and frontend if frontend code exists.
- Keep business logic independent from infrastructure, UI, transport, and database details.

### 3. Domain Purity
- The domain core must remain pure.
- Domain code must not depend on:
  - databases
  - Neo4j drivers
  - HTTP frameworks
  - UI frameworks
  - file I/O
  - environment/config access
  - concrete adapters
  - infrastructure logging setup
- Domain code may contain only:
  - entities
  - value objects
  - domain services
  - domain events
  - invariants
  - domain exceptions
  - domain-owned contracts

### 4. Prefer IF-Less Design
- Prefer strategy-based, registry-based, polymorphic, command-based, or rule-based dispatching.
- Avoid long `if/elif/else` or `match/case` chains in domain and application core.
- Small guard clauses are acceptable, but branching must not dominate the design.

### 5. Prefer Explicit Behavioral Patterns
When behavior varies by type, mode, state, source, or command, prefer:
- Strategy Pattern
- Command Pattern
- State Pattern
- policy objects
- dispatch maps
- registries

Do not encode volatile behavior in large nested condition trees.

### 6. Centralized Logging Only
- Logging must follow the project’s central logging concept.
- Do not add ad-hoc logging helpers in random modules.
- Do not place logging utilities in semantically wrong folders.
- Do not pollute domain logic with infrastructure logging concerns.
- Do not use `print()` as application logging except in minimal bootstrap code or throwaway local scripts explicitly marked as such.

### 7. Single Composition Root
- Concrete object wiring must happen in one composition root.
- Bind concrete adapters there.
- Do not scatter object creation across the codebase.
- Do not instantiate infrastructure dependencies directly in domain or use-case code.

### 8. Comments and Explanations
- Source-code comments must be written in **English**.
- User-facing explanations must be written in **German**.
- Keep comments concise and useful.
- Do not add decorative or obvious comments.

### 9. Quality Gate
Before considering a task finished, Codex must:
- run linting if available
- run tests if available
- run project verification commands if defined
- report violations honestly
- propose compliant refactorings instead of patching around architectural problems

---

## Layer Responsibilities

### Domain Layer
Allowed:
- entities
- value objects
- domain services
- domain events
- invariants
- domain exceptions
- domain-owned ports

Forbidden:
- database access
- Cypher queries
- Neo4j driver usage
- HTTP code
- React/UI code
- file handling
- environment access
- framework-specific code
- concrete repositories
- concrete clients
- infrastructure concerns

### Application Layer
Allowed:
- use cases
- application services
- orchestration
- command/query models
- application DTOs
- coordination of ports
- mapping between application models and domain models

Forbidden:
- direct driver usage
- direct database access
- direct Cypher usage
- concrete adapter wiring
- framework-heavy transport logic
- hidden business logic in controllers or repositories

### Ports
Ports are contracts between the core and the outside.

#### Inbound Ports
- define how the application is invoked
- must be minimal
- must be technology-agnostic
- must express intent, not transport details

#### Outbound Ports
- define what the application needs from external systems
- must be minimal and stable
- must not leak vendor or driver types
- must not expose infrastructure semantics unless unavoidable

### Primary Adapters
Examples:
- CLI
- HTTP controllers
- message consumers
- scheduled triggers
- test harnesses

Responsibilities:
- receive external input
- validate transport-level structure
- map transport models into application input
- call inbound ports
- map results into transport responses

Forbidden:
- domain rule implementation
- business decisions
- bypassing application services

### Secondary Adapters
Examples:
- Neo4j repositories
- HTTP API clients
- event publishers
- file import/export adapters

Responsibilities:
- implement outbound ports
- isolate technical libraries and vendors
- map technical data to application-facing models
- translate technical failures appropriately

Forbidden:
- business rule decisions
- use-case orchestration

### Infrastructure Layer
Allowed:
- configuration
- bootstrap
- dependency wiring
- factories
- driver/session/connection management
- environment-specific assembly
- central logging setup
- tracing/correlation setup

Forbidden:
- business logic
- domain decisions
- use-case logic disguised as infrastructure

---

## Dependency Rules

### Inward Dependency Rule
Allowed:
- adapters -> application/domain ports
- infrastructure -> adapters/application/domain
- application -> domain
- domain -> internal domain code only

Forbidden:
- domain -> application
- domain -> adapters
- domain -> infrastructure
- application -> concrete adapters
- ports -> concrete implementations

### Concrete Type Rule
- Depend on abstractions, not implementations.
- Do not import concrete adapter classes into domain or application core.
- Do not reference infrastructure modules from domain code.

---

## Persistence Rules

### Repository Rule
- Repository interfaces belong to the core contract side as outbound ports.
- Repository implementations belong to secondary adapters.
- Repositories must not expose driver-specific results to the core.

### Neo4j Rule
If Neo4j is used:
- Cypher stays outside domain and application core
- driver/session handling belongs to infrastructure or outbound adapters
- graph-to-domain mapping belongs at the adapter boundary
- session lifecycle must not leak into use cases

### Connection Management Rule
- Connection factories, session providers, and driver lifecycle belong to infrastructure.
- They must be reusable and centrally wired.
- They must not be created ad hoc throughout the codebase.

---

## Error Handling Rules

### Domain Errors
- Represent business violations explicitly.
- Do not wrap domain logic in infrastructure error semantics.

### Application Errors
- Coordinate failures across use cases.
- Translate port failures into meaningful application outcomes.

### Adapter Errors
- Catch and translate technical exceptions.
- Do not leak raw driver/framework exceptions into the core unless explicitly wrapped.

---

## Testing Rules

### Domain Tests
- Must test pure business rules in isolation.
- Must not require infrastructure.

### Application Tests
- Must test use-case orchestration against mocked, fake, or stubbed ports.

### Adapter Tests
- Must verify adapter compliance with port contracts.
- May run against real infrastructure where appropriate.

### End-to-End Tests
- Must validate full flows from primary adapter through application to secondary adapters.

### Test Double Rule
- Fakes, mocks, and stubs must implement the same ports as production adapters.

---

## File Placement Rules

Codex must place files by responsibility, not convenience.

Illustrative structure:

```text
src/
  domain/
    entities/
    value_objects/
    services/
    events/
    exceptions/
    ports/

  application/
    use_cases/
    services/
    commands/
    queries/
    dto/

  adapters/
    inbound/
      cli/
      http/
      messaging/
    outbound/
      persistence/
      external_services/
      messaging/

  infrastructure/
    configuration/
    logging/
    context/
    bootstrap/
    factories/