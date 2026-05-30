from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_company_service
from app.core.errors import NotFoundError
from app.models.company import Company, CompanyCreate
from app.models.risk import CompanyRiskResponse
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=Company, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    service: CompanyService = Depends(get_company_service),
) -> Company:
    return service.create_company(payload)


@router.get("/{company_id}", response_model=Company)
def get_company(
    company_id: UUID,
    service: CompanyService = Depends(get_company_service),
) -> Company:
    try:
        return service.get_company(company_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{company_id}/risk", response_model=CompanyRiskResponse)
def get_company_risk(
    company_id: UUID,
    max_paths: int | None = Query(default=None, ge=1, le=100),
    service: CompanyService = Depends(get_company_service),
) -> CompanyRiskResponse:
    try:
        return service.get_risk_exposure(company_id, max_paths=max_paths)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
