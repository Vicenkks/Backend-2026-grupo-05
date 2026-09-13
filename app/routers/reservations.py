from math import ceil

from fastapi import APIRouter, HTTPException, Response, status

from app.repositories.instances import company_repository, reservation_repository, space_repository
from app.schemas.reservation import ReservationCreate, ReservationUpdate
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservations"])
service = ReservationService(reservation_repository, space_repository, company_repository)


def _serialize(reservation):
	return {"reservationId": reservation.reservationId, "spaceId": reservation.spaceId, "companyId": reservation.companyId, "start_date": reservation.start_date.isoformat(), "end_date": reservation.end_date.isoformat(), "status": reservation.status.value, "reason": reservation.reason, "created_at": reservation.created_at.isoformat(), "updated_at": reservation.updated_at.isoformat()}


def _handle_error(error: Exception) -> None:
	if isinstance(error, LookupError):
		raise HTTPException(status_code=404, detail={"code": "RESOURCE_NOT_FOUND", "message": str(error), "details": []}) from error
	if "already reserved" in str(error):
		raise HTTPException(status_code=409, detail={"code": "CONFLICT", "message": str(error), "details": []}) from error
	raise HTTPException(status_code=400, detail={"code": "BUSINESS_RULE_VIOLATION", "message": str(error), "details": []}) from error


@router.post("", status_code=status.HTTP_201_CREATED)
def create_reservation(data: ReservationCreate):
	try:
		return _serialize(service.create(data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.get("")
def list_reservations(page: int = 1, limit: int = 20, sort_by: str = "created_at", direction: str = "desc", company_id: str | None = None, status: str | None = None):
	if page < 1 or not 1 <= limit <= 100 or direction not in {"asc", "desc"}:
		raise HTTPException(status_code=422, detail="Invalid pagination parameters")
	reservations = service.get_all()
	if company_id is not None:
		reservations = [item for item in reservations if item.companyId == company_id]
	if status is not None:
		reservations = [item for item in reservations if item.status.value == status]
	if not all(hasattr(item, sort_by) for item in reservations):
		raise HTTPException(status_code=422, detail="Invalid sort field")
	reservations.sort(key=lambda item: getattr(item, sort_by), reverse=direction == "desc")
	total = len(reservations)
	start = (page - 1) * limit
	return {"items": [_serialize(item) for item in reservations[start:start + limit]], "total": total, "page": page, "limit": limit, "total_pages": ceil(total / limit) if total else 0}


@router.get("/{reservation_id}")
def get_reservation(reservation_id: str):
	try:
		return _serialize(service.get_by_id(reservation_id))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.put("/{reservation_id}")
def update_reservation(reservation_id: str, data: ReservationUpdate):
	try:
		return _serialize(service.update(reservation_id, data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: str) -> Response:
	try:
		service.delete(reservation_id)
	except (LookupError, ValueError) as error:
		_handle_error(error)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
