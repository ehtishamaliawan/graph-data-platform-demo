from dataclasses import dataclass
from datetime import UTC, datetime

from app.db.neo4j import Neo4jClient


@dataclass(frozen=True)
class Migration:
    migration_id: str
    statements: tuple[str, ...]


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        migration_id="001_uuid_constraints",
        statements=(
            "CREATE CONSTRAINT company_id_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT employee_id_unique IF NOT EXISTS FOR (e:Employee) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT domain_id_unique IF NOT EXISTS FOR (d:Domain) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT threat_id_unique IF NOT EXISTS FOR (t:Threat) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT migration_id_unique IF NOT EXISTS FOR (m:Migration) REQUIRE m.id IS UNIQUE",
        ),
    ),
)


def apply_migrations(client: Neo4jClient) -> None:
    client.run_statements(
        "bootstrap_migration_constraint",
        ["CREATE CONSTRAINT migration_id_unique IF NOT EXISTS FOR (m:Migration) REQUIRE m.id IS UNIQUE"],
    )

    for migration in MIGRATIONS:
        existing = client.execute_read(
            "check_migration",
            "MATCH (m:Migration {id: $id}) RETURN m.id AS id",
            {"id": migration.migration_id},
        )
        if existing:
            continue

        client.run_statements(f"migration_{migration.migration_id}", migration.statements)
        client.execute_write(
            "record_migration",
            "CREATE (m:Migration {id: $id, applied_at: $applied_at})",
            {"id": migration.migration_id, "applied_at": datetime.now(UTC).isoformat()},
        )
