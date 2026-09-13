from math import ceil

from fastapi import APIRouter, HTTPException, Response, status

from app.repositories.instances import company_repository
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"])
service = CompanyService(company_repository)


def _serialize(company):
	return {"companyId": company.companyId, "companyName": company.companyName, "rut": company.rut, "email": company.email, "phone": company.phone, "address": company.address, "created_at": company.created_at.isoformat(), "updated_at": company.updated_at.isoformat()}


def _handle_error(error: Exception) -> None:
	if isinstance(error, LookupError):
		raise HTTPException(status_code=404, detail={"code": "RESOURCE_NOT_FOUND", "message": str(error), "details": []}) from error
	raise HTTPException(status_code=400, detail={"code": "BUSINESS_RULE_VIOLATION", "message": str(error), "details": []}) from error


@router.post("", status_code=status.HTTP_201_CREATED)
def create_company(data: CompanyCreate):
	try:
		return _serialize(service.create(data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.get("")
def list_companies(page: int = 1, limit: int = 20, sort_by: str = "created_at", direction: str = "desc"):
	if page < 1 or not 1 <= limit <= 100 or direction not in {"asc", "desc"}:
		raise HTTPException(status_code=422, detail="Invalid pagination parameters")
	companies = service.get_all()
	if not all(hasattr(company, sort_by) for company in companies):
		raise HTTPException(status_code=422, detail="Invalid sort field")
	companies.sort(key=lambda company: getattr(company, sort_by), reverse=direction == "desc")
	total = len(companies)
	start = (page - 1) * limit
	return {"items": [_serialize(company) for company in companies[start:start + limit]], "total": total, "page": page, "limit": limit, "total_pages": ceil(total / limit) if total else 0}


@router.get("/{company_id}")
def get_company(company_id: str):
	try:
		return _serialize(service.get_by_id(company_id))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.put("/{company_id}")
def update_company(company_id: str, data: CompanyUpdate):
	try:
		return _serialize(service.update(company_id, data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: str) -> Response:
	try:
		service.delete(company_id)
	except (LookupError, ValueError) as error:
		_handle_error(error)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
