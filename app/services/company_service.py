from uuid import UUID

from app.core.errors import NotFoundError
from app.models.company import Company, CompanyCreate
from app.models.risk import CompanyRiskResponse
from app.repositories.company_repository import CompanyRepository


class CompanyService:
    def __init__(self, repository: CompanyRepository, risk_max_paths: int) -> None:
        self._repository = repository
        self._risk_max_paths = risk_max_paths

    def create_company(self, payload: CompanyCreate) -> Company:
        return self._repository.create(payload)

    def get_company(self, company_id: UUID) -> Company:
        company = self._repository.get_by_id(company_id)
        if company is None:
            raise NotFoundError("Company not found")
        return company

    def get_risk_exposure(self, company_id: UUID, max_paths: int | None = None) -> CompanyRiskResponse:
        effective_limit = self._risk_max_paths if max_paths is None else max_paths
        _ = self.get_company(company_id)
        return self._repository.get_company_risk(company_id, effective_limit)
