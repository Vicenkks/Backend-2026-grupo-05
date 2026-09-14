from math import ceil

from fastapi import APIRouter, HTTPException, Response, status

from app.repositories.instances import company_repository, reservation_repository
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"], responses={400: {"description": "Business rule error"}, 404: {"description": "Company not found"}, 409: {"description": "Related reservations conflict"}, 422: {"description": "Invalid data"}})
service = CompanyService(company_repository, reservation_repository)


def _serialize(company):
	return {"companyId": company.companyId, "companyName": company.companyName, "rut": company.rut, "email": company.email, "phone": company.phone, "address": company.address, "created_at": company.created_at.isoformat(), "updated_at": company.updated_at.isoformat()}


def _handle_error(error: Exception) -> None:
	if isinstance(error, LookupError):
		raise HTTPException(status_code=404, detail={"code": "RESOURCE_NOT_FOUND", "message": str(error), "details": []}) from error
	if "Cannot delete" in str(error):
		raise HTTPException(status_code=409, detail={"code": "CONFLICT", "message": str(error), "details": []}) from error
	raise HTTPException(status_code=400, detail={"code": "BUSINESS_RULE_VIOLATION", "message": str(error), "details": []}) from error


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CompanyResponse)
def create_company(data: CompanyCreate):
	"""Create a new company."""
	try:
		return _serialize(service.create(data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.get("")
def list_companies(page: int = 1, limit: int = 20, sort_by: str = "created_at", direction: str = "desc"):
	"""List companies using sorting and pagination."""
	if page < 1 or not 1 <= limit <= 100 or direction not in {"asc", "desc"}:
		raise HTTPException(status_code=422, detail="Invalid pagination parameters")
	if sort_by not in {"companyName", "rut", "email", "phone", "address", "created_at", "updated_at"}:
		raise HTTPException(status_code=422, detail="Invalid sort field")
	companies = service.get_all()
	companies.sort(key=lambda company: getattr(company, sort_by), reverse=direction == "desc")
	total = len(companies)
	start = (page - 1) * limit
	return {"items": [_serialize(company) for company in companies[start:start + limit]], "total": total, "page": page, "limit": limit, "total_pages": ceil(total / limit) if total else 0}


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: str):
	"""Get one company by its ID."""
	try:
		return _serialize(service.get_by_id(company_id))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: str, data: CompanyUpdate):
	"""Update an existing company."""
	try:
		return _serialize(service.update(company_id, data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: str) -> Response:
	"""Delete a company when it has no reservations."""
	try:
		service.delete(company_id)
	except (LookupError, ValueError) as error:
		_handle_error(error)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
