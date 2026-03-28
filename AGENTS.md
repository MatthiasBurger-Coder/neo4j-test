# Project Rules

## Architecture
- Hexagonal architecture is mandatory in backend and frontend.
- Keep domain logic independent from infrastructure, UI, and database details.
- Do not couple domain code directly to Neo4j, HTTP, or React.

## Coding Style
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