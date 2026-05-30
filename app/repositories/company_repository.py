from abc import ABC, abstractmethod
from uuid import UUID

from app.db.neo4j import Neo4jClient
from app.models.company import Company, CompanyCreate
from app.models.risk import CompanyRiskResponse, PathNode, PathRelationship, RiskPath


class CompanyRepository(ABC):
    @abstractmethod
    def create(self, payload: CompanyCreate) -> Company:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, company_id: UUID) -> Company | None:
        raise NotImplementedError

    @abstractmethod
    def get_company_risk(self, company_id: UUID, max_paths: int) -> CompanyRiskResponse:
        raise NotImplementedError


class Neo4jCompanyRepository(CompanyRepository):
    def __init__(self, client: Neo4jClient) -> None:
        self._client = client

    def create(self, payload: CompanyCreate) -> Company:
        record = self._client.execute_write(
            "create_company",
            """
            CREATE (c:Company {id: randomUUID(), name: $name, created_at: datetime().toString()})
            RETURN c.id AS id, c.name AS name, c.created_at AS created_at
            """,
            {"name": payload.name},
        )[0]
        return Company.model_validate(record.data())

    def get_by_id(self, company_id: UUID) -> Company | None:
        rows = self._client.execute_read(
            "get_company",
            """
            MATCH (c:Company {id: $id})
            RETURN c.id AS id, c.name AS name, c.created_at AS created_at
            LIMIT 1
            """,
            {"id": str(company_id)},
        )
        if not rows:
            return None
        return Company.model_validate(rows[0].data())

    def get_company_risk(self, company_id: UUID, max_paths: int) -> CompanyRiskResponse:
        rows = self._client.execute_read(
            "company_risk_paths",
            """
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
            RETURN
              score,
              [n IN nodes(path) | {
                id: coalesce(n.id, ''),
                label: head(labels(n)),
                name: coalesce(n.name, n.email, n.domain, n.title, '')
              }] AS nodes,
              [r IN relationships(path) | {type: type(r)}] AS relationships
            LIMIT $max_paths
            """,
            {"company_id": str(company_id), "max_paths": max_paths},
        )

        paths: list[RiskPath] = []
        total = 0.0
        for row in rows:
            raw = row.data()
            score = float(raw["score"])
            total += score
            paths.append(
                RiskPath(
                    score=score,
                    nodes=[PathNode(**node) for node in raw["nodes"]],
                    relationships=[PathRelationship(**rel) for rel in raw["relationships"]],
                )
            )

        return CompanyRiskResponse(
            company_id=str(company_id),
            total_score=round(total, 3),
            path_count=len(paths),
            truncated=len(paths) >= max_paths,
            paths=paths,
        )
