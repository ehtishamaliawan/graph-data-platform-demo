from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.db.neo4j import Neo4jClient
from app.repositories.company_repository import CompanyRepository, Neo4jCompanyRepository
from app.services.company_service import CompanyService


def get_neo4j_client(request: Request) -> Neo4jClient:
    return request.app.state.neo4j_client


def get_company_repository(client: Neo4jClient = Depends(get_neo4j_client)) -> CompanyRepository:
    return Neo4jCompanyRepository(client)


def get_company_service(
    repository: CompanyRepository = Depends(get_company_repository),
    settings: Settings = Depends(get_settings),
) -> CompanyService:
    return CompanyService(repository, risk_max_paths=settings.risk_max_paths)
