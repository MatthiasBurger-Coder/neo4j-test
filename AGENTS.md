# Project Rules

## Architecture
- Hexagonal architecture is mandatory in backend and frontend.
- Keep domain logic independent from infrastructure, UI, and database details.
- Do not couple domain code directly to Neo4j, HTTP, or React.

## Coding Style
- Use Hexagonal architecture principles.
- Prefer if-less design where reasonable.
- Prefer Strategy Pattern, Command Pattern, State Pattern, and rule-based dispatching.
- Avoid long if/else or switch chains in domain and application core.

## Frontend
- React is a UI and wiring layer, not a business-logic container.
- Keep domain logic, use cases, adapters, and UI separated.

## Backend
- Use ports and adapters consistently.
- Keep persistence behind adapters.
- No direct Cypher or Neo4j driver usage in domain classes.

## Language Rules
- Write code comments in English.
- Write user-facing explanations in German.

## Quality Gates
- Run lint, tests, and project verification commands before finishing.
- If architecture rules are violated, propose a compliant refactoring instead of patching around them.

# AGENTS.md
**Mandatory Working Rules for Codex Agents in this Project**

---

## Purpose
This file defines the mandatory rules all Codex agents must follow when reading, generating, modifying, or reviewing source code in this repository.

The project is built on **strict hexagonal architecture**.  
These rules are **binding**.  
If an implementation idea conflicts with this document, this document wins.

---

## Project-Wide Non-Negotiable Rules

### 1. Language and Technology
- The implementation language is **Python**.
- Do not introduce another main language for backend logic.
- Do not introduce framework-driven architecture unless explicitly required.
- Keep the codebase framework-light and architecture-first.

### 2. Architectural Style
- The entire project must follow **hexagonal architecture**.
- This applies **consistently** across all layers and modules.
- The same architectural discipline must be respected in backend and frontend if frontend code exists.

### 3. Domain Protection
- The **domain core must remain pure**.
- Domain code must not depend on:
  - databases
  - web frameworks
  - ORMs
  - message brokers
  - environment configuration
  - logging libraries with infrastructure coupling
  - concrete adapters
- Domain code may only express:
  - business rules
  - invariants
  - entities
  - value objects
  - domain services
  - domain events
  - domain-level abstractions and contracts

### 4. Prefer IF-Less Design
- Prefer **strategy-based**, polymorphic, registry-based, or dispatch-based solutions over long `if/elif/else` chains.
- Use explicit behavior objects instead of procedural branching where reasonable.
- Avoid encoding business rules in control-flow-heavy code.
- A small guard clause is acceptable if it improves clarity, but branching must not become the dominant design style.

### 5. Prefer Strategy Pattern
- When behavior varies by type, state, source, command, or mode, prefer:
  - strategy objects
  - registries
  - dispatch maps
  - command objects
  - policy objects
- Do not implement volatile business behavior as large nested condition trees.

### 6. Centralized Logging Only
- Logging must be centralized.
- Do not invent local ad-hoc logging utilities inside random modules.
- Do not place logging helper modules in unrelated packages.
- Use the project’s central logging approach only.
- Logging must not pollute domain logic with infrastructure details.

### 7. Composition Root Discipline
- Object wiring happens in **one composition root**.
- Concrete adapters must be bound there.
- Do not scatter object construction across the codebase.
- Do not instantiate infrastructure dependencies directly inside domain code or use-case code unless explicitly part of a factory in the correct layer.

### 8. Human-Maintainable Code
- Code must be readable, explicit, and maintainable.
- Avoid cleverness that hides intent.
- Prefer small focused classes and functions.
- Prefer explicit names over short cryptic names.

### 9. Comments and Documentation
- All source-code comments must be written in **English**.
- Docstrings and inline comments must be concise and useful.
- Do not add decorative comments.
- Do not explain obvious code.

---

## Required Architectural Structure

Codex agents must organize code along the following boundaries.

### Domain Layer
Contains pure business logic only.

Allowed contents:
- entities
- value objects
- domain services
- domain rules
- invariants
- domain events
- domain exceptions
- port definitions if they are domain-owned contracts

Forbidden:
- database access
- HTTP logic
- file I/O
- framework annotations or framework base classes
- environment access
- concrete repositories
- concrete clients
- infrastructure logging setup
- transport models tied to external systems

### Application Layer
Contains use cases and orchestration.

Allowed contents:
- application services
- use cases
- command/query models
- orchestration logic
- transaction boundary coordination where applicable
- port consumption
- mapping between application models and domain models

Forbidden:
- concrete infrastructure code
- database driver usage
- framework-heavy controller logic
- domain rule leakage into adapters
- direct wiring of implementations

### Ports
Ports are contracts between the core and the outside.

#### Inbound Ports
Define how the application is invoked.

Examples:
- create person use case
- load relationship graph use case
- register event use case

Rules:
- keep them minimal
- keep them technology-agnostic
- express intent, not transport concerns

#### Outbound Ports
Define what the application needs from the outside.

Examples:
- repository contracts
- graph persistence contracts
- external news provider contracts
- market data provider contracts
- event publisher contracts

Rules:
- keep them minimal and stable
- do not leak driver-specific types
- do not expose infrastructure semantics unless unavoidable

### Adapters Layer
Contains technical implementations of ports.

#### Primary Adapters
Drive the application.

Examples:
- CLI
- REST controller
- message consumer
- batch trigger
- test harness

Responsibilities:
- parse input
- validate transport-level structure
- map transport data into application input models
- invoke inbound ports
- map results into transport responses

Forbidden:
- business decisions
- domain rule implementation
- direct persistence logic bypassing application services

#### Secondary Adapters
Implement outbound ports.

Examples:
- Neo4j repository
- HTTP API client
- event bus producer
- file-based import/export adapter

Responsibilities:
- translate application requests into technical calls
- isolate vendor, framework, and driver specifics
- map technical failures into meaningful application-facing outcomes

Forbidden:
- domain decision logic
- use-case orchestration

### Infrastructure Layer
Contains technical setup and composition root.

Allowed contents:
- configuration loading
- dependency injection wiring
- bootstrap/application startup
- driver factories
- session/connection factories
- environment-specific assembly

Forbidden:
- core business rules
- leaking infra concerns into domain

---

## Dependency Rules

### Inward Dependency Rule
All dependencies must point inward.

Allowed direction:
- adapters -> application/domain ports
- infrastructure -> adapters/application/domain
- application -> domain
- domain -> nothing external

Forbidden direction:
- domain -> application
- domain -> adapters
- domain -> infrastructure
- application -> concrete adapters
- ports -> concrete implementations

### Concrete Type Rule
- Depend on abstractions, not implementations.
- Do not reference concrete adapter classes from domain code.
- Do not import infrastructure modules into domain or application core.

---

## Codex Agent Behavioral Rules

### When Creating Code
Codex must:
- place code in the correct architectural layer
- create ports before adapters when introducing new external interactions
- keep interfaces/contracts minimal
- prefer composition over inheritance unless inheritance is clearly justified
- create focused files with one architectural responsibility

Codex must not:
- place repositories inside the domain if they are concrete implementations
- mix application orchestration with database code
- place technical helpers in arbitrary folders
- hide architectural violations behind convenience shortcuts

### When Reviewing Code
Codex must actively check:
- whether the file is located in the correct layer
- whether imports violate hexagonal boundaries
- whether business logic has leaked into adapters
- whether wiring is centralized
- whether a strategy-based design would be better than branching
- whether logging is improperly duplicated or misplaced

If violations exist, Codex must propose:
1. the violation
2. why it violates the architecture
3. the target location/design
4. the exact refactoring direction

### When Refactoring
Codex must preserve behavior while improving structure.

Refactoring priorities:
1. restore hexagonal boundaries
2. remove misplaced infrastructure code
3. isolate ports
4. extract strategies from conditional logic
5. centralize wiring
6. centralize logging usage
7. simplify file/module responsibilities

---

## Repository and Persistence Rules

### Repository Rule
- Repository interfaces belong to the core contract side, usually as outbound ports.
- Repository implementations belong to secondary adapters.
- Repositories must not expose database-driver-specific results to the core.

### Neo4j Rule
If Neo4j is used:
- driver/session handling belongs to infrastructure or adapter implementation
- Cypher and database specifics must remain outside the domain
- mapping between graph persistence shape and domain/application models belongs in the adapter boundary
- session lifecycle management must not leak into use cases

### Connection Management Rule
- Connection factories, session providers, and driver lifecycle belong to infrastructure.
- They must be reusable and centrally wired.
- They must not be instantiated ad hoc across the codebase.

---

## Logging and Observability Rules

- Use one central logging concept for the whole project.
- Do not create duplicate logging wrappers in feature folders.
- Correlation and trace context belong to the correct technical boundary, not to arbitrary business modules.
- Logging must support traceability without coupling the domain to infrastructure details.
- Structured logging is preferred over unstructured debug prints.
- Do not use `print()` for application logging except in minimal bootstrap or local throwaway scripts explicitly marked as such.

---

## Error Handling Rules

### Domain Errors
- Represent business violations explicitly.
- Do not wrap domain rules in infrastructure exception semantics.

### Application Errors
- Coordinate failures across use cases.
- Map outbound port failures into meaningful application-level outcomes.

### Adapter Errors
- Catch and translate technical exceptions.
- Do not leak raw driver/framework errors into the core unless explicitly wrapped.

---

## Testing Rules

### Domain Tests
- Must test pure business logic in isolation.
- Must not require infrastructure.

### Application Tests
- Must verify use-case orchestration against mocked or fake ports.

### Adapter Tests
- Must verify that adapters fulfill port contracts.
- Integration tests may use real infrastructure.

### End-to-End Tests
- Must validate real flows through primary adapter -> application -> secondary adapter.

### Test Double Rule
- Fakes, mocks, and stubs must implement the same ports as production adapters.

---

## File Placement Rules

Codex must place files according to responsibility, not convenience.

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
