from datetime import UTC, datetime
from unittest.mock import create_autospec
from uuid import uuid4

import pytest

from app.core.errors import NotFoundError
from app.models.company import Company, CompanyCreate
from app.models.risk import CompanyRiskResponse
from app.repositories.company_repository import CompanyRepository
from app.services.company_service import CompanyService


@pytest.fixture
def repository_mock() -> CompanyRepository:
    return create_autospec(CompanyRepository, instance=True)


def test_create_company_uses_repository(repository_mock: CompanyRepository) -> None:
    company = Company(id=uuid4(), name="Acme", created_at=datetime.now(UTC))
    repository_mock.create.return_value = company
    service = CompanyService(repository_mock, risk_max_paths=25)

    created = service.create_company(CompanyCreate(name="Acme"))

    assert created == company
    repository_mock.create.assert_called_once()


def test_get_company_not_found_raises(repository_mock: CompanyRepository) -> None:
    repository_mock.get_by_id.return_value = None
    service = CompanyService(repository_mock, risk_max_paths=25)

    with pytest.raises(NotFoundError):
        service.get_company(uuid4())


def test_get_risk_exposure_validates_limit(repository_mock: CompanyRepository) -> None:
    company_id = uuid4()
    repository_mock.get_by_id.return_value = Company(id=company_id, name="Acme", created_at=datetime.now(UTC))
    repository_mock.get_company_risk.return_value = CompanyRiskResponse(
        company_id=str(company_id),
        total_score=1.0,
        path_count=1,
        paths=[],
    )
    service = CompanyService(repository_mock, risk_max_paths=25)

    with pytest.raises(ValueError):
        service.get_risk_exposure(company_id, max_paths=0)
