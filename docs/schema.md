# Neo4j Schema

## Node labels and properties
| Label | Key properties | Purpose |
| --- | --- | --- |
| `Company` | `id` (UUID string), `name`, `created_at` | Primary entity for risk analysis and API lookups. |
| `Employee` | `id` (UUID string), `name`, `email`, `title` | Workforce nodes used in threat-to-company paths. |
| `Domain` | `id` (UUID string), `domain` | Corporate domains tied to employees and ownership. |
| `Threat` | `id` (UUID string), `name`, `severity` (optional) | Threat intelligence nodes linked to companies or domains. |
| `Migration` | `id`, `applied_at` | Records schema migrations executed at startup. |

> The API uses `coalesce(n.name, n.email, n.domain, n.title, '')` when rendering risk paths, so those properties are expected on their respective nodes.

## Relationship types
| Relationship | From -> To | Meaning |
| --- | --- | --- |
| `WORKS_FOR` | `Employee` → `Company` | Employment relationship. |
| `USES` | `Employee` → `Domain` | Employee uses/accesses a domain. |
| `OWNS` | `Company` → `Domain` | Company owns a domain. |
| `TARGETS` | `Threat` → `Company` or `Domain` | Threat targets an entity or a domain. |

## Constraints (implemented via migrations)
```cypher
CREATE CONSTRAINT company_id_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT employee_id_unique IF NOT EXISTS FOR (e:Employee) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT domain_id_unique IF NOT EXISTS FOR (d:Domain) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT threat_id_unique IF NOT EXISTS FOR (t:Threat) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT migration_id_unique IF NOT EXISTS FOR (m:Migration) REQUIRE m.id IS UNIQUE;
```

## Recommended indexes for production
```cypher
CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name);
CREATE INDEX domain_value IF NOT EXISTS FOR (d:Domain) ON (d.domain);
CREATE INDEX employee_email IF NOT EXISTS FOR (e:Employee) ON (e.email);
```

## Example graph dataset
```cypher
CREATE (c:Company {id: '11111111-1111-1111-1111-111111111111', name: 'Northwind Logistics', created_at: '2025-01-01T00:00:00Z'})
CREATE (d1:Domain {id: '22222222-2222-2222-2222-222222222222', domain: 'northwind.com'})
CREATE (d2:Domain {id: '33333333-3333-3333-3333-333333333333', domain: 'northwind-logistics.com'})
CREATE (e1:Employee {id: '44444444-4444-4444-4444-444444444444', name: 'Jules Ortega', email: 'jules@northwind.com', title: 'Security Engineer'})
CREATE (e2:Employee {id: '55555555-5555-5555-5555-555555555555', name: 'Rina Patel', email: 'rina@northwind.com', title: 'IT Manager'})
CREATE (t1:Threat {id: '66666666-6666-6666-6666-666666666666', name: 'Credential stuffing', severity: 'high'})
CREATE (t2:Threat {id: '77777777-7777-7777-7777-777777777777', name: 'Typosquat campaign', severity: 'medium'})
CREATE (t3:Threat {id: '88888888-8888-8888-8888-888888888888', name: 'Direct ransomware', severity: 'critical'})
CREATE (e1)-[:WORKS_FOR]->(c)
CREATE (e2)-[:WORKS_FOR]->(c)
CREATE (e1)-[:USES]->(d1)
CREATE (e2)-[:USES]->(d2)
CREATE (c)-[:OWNS]->(d1)
CREATE (c)-[:OWNS]->(d2)
CREATE (t1)-[:TARGETS]->(d1)
CREATE (t2)-[:TARGETS]->(d2)
CREATE (t3)-[:TARGETS]->(c);
```

## Example Cypher queries
### Fetch a company by ID
```cypher
MATCH (c:Company {id: $company_id})
RETURN c.id AS id, c.name AS name, c.created_at AS created_at;
```

### List domains and employees for a company
```cypher
MATCH (c:Company {id: $company_id})
OPTIONAL MATCH (c)<-[:WORKS_FOR]-(e:Employee)
OPTIONAL MATCH (c)-[:OWNS]->(d:Domain)
RETURN c.name AS company, collect(DISTINCT e.email) AS employees, collect(DISTINCT d.domain) AS domains;
```

### Risk paths (bounded traversal used by the API)
```cypher
MATCH (c:Company {id: $company_id})
CALL {
  WITH c
  MATCH p=(t:Threat)-[:TARGETS]->(c)
  RETURN p AS path, 1.0 AS score
  UNION ALL
  WITH c
  MATCH p=(t:Threat)-[:TARGETS]->(d:Domain)<-[:USES]-(e:Employee)-[:WORKS_FOR]->(c)
  RETURN p AS path, 0.7 AS score
  UNION ALL
  WITH c
  MATCH p=(t:Threat)-[:TARGETS]->(d:Domain)<-[:OWNS]-(c)
  RETURN p AS path, 0.5 AS score
}
RETURN score, nodes(path) AS nodes, relationships(path) AS relationships
LIMIT $limit;
```
