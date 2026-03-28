# neo4j-test

Small playground project for testing Neo4j data modeling and query patterns.

## Can this be filled with a Cypher query?

Yes — you can populate the graph directly with Cypher using `CREATE`, `MERGE`, and `UNWIND`.

### Example: insert city, street, building, and address

```cypher
MERGE (c:City {name: 'Berlin'})
MERGE (s:Street {name: 'Unter den Linden'})
MERGE (b:Building {number: '77'})
MERGE (a:Address {id: 'addr-001'})
MERGE (c)-[:HAS_STREET]->(s)
MERGE (s)-[:HAS_BUILDING]->(b)
MERGE (b)-[:HAS_ADDRESS]->(a);
```

### Example: bulk import with `UNWIND`

```cypher
UNWIND [
  {id: 'addr-001', city: 'Berlin', street: 'Unter den Linden', number: '77'},
  {id: 'addr-002', city: 'Berlin', street: 'Friedrichstraße', number: '12'}
] AS row
MERGE (c:City {name: row.city})
MERGE (s:Street {name: row.street})
MERGE (b:Building {number: row.number})
MERGE (a:Address {id: row.id})
MERGE (c)-[:HAS_STREET]->(s)
MERGE (s)-[:HAS_BUILDING]->(b)
MERGE (b)-[:HAS_ADDRESS]->(a);
```

### Tip

Use `MERGE` (instead of only `CREATE`) for idempotent imports, so running the same query multiple times does not duplicate nodes.
