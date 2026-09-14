from fastapi import APIRouter, HTTPException, Response, status

from app.repositories.instances import availability_repository, space_repository
from app.schemas.availability import AvailabilityCreate, AvailabilityResponse, AvailabilityUpdate
from app.services.availability_service import AvailabilityService

router = APIRouter(prefix="/availabilities", tags=["Availabilities"], responses={400: {"description": "Business rule error"}, 404: {"description": "Availability not found"}, 422: {"description": "Invalid data"}})
service = AvailabilityService(availability_repository, space_repository)


def _serialize(availability):
	return {
		"availabilityId": availability.availabilityId,
		"spaceId": availability.spaceId,
		"weekday": availability.weekday.value,
		"opening_time": availability.opening_time.isoformat(),
		"closing_time": availability.closing_time.isoformat(),
		"created_at": availability.created_at.isoformat(),
		"updated_at": availability.updated_at.isoformat(),
	}


def _handle_error(error: Exception) -> None:
	if isinstance(error, LookupError):
		raise HTTPException(status_code=404, detail={"code": "RESOURCE_NOT_FOUND", "message": str(error), "details": []}) from error
	raise HTTPException(status_code=400, detail={"code": "BUSINESS_RULE_VIOLATION", "message": str(error), "details": []}) from error


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AvailabilityResponse)
def create_availability(data: AvailabilityCreate):
	try:
		return _serialize(service.create(data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.get("", response_model=list[AvailabilityResponse])
def list_availabilities():
	return [_serialize(item) for item in service.get_all()]


@router.get("/{availability_id}", response_model=AvailabilityResponse)
def get_availability(availability_id: str):
	try:
		return _serialize(service.get_by_id(availability_id))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.put("/{availability_id}", response_model=AvailabilityResponse)
def update_availability(availability_id: str, data: AvailabilityUpdate):
	try:
		return _serialize(service.update(availability_id, data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(availability_id: str) -> Response:
	try:
		service.delete(availability_id)
	except (LookupError, ValueError) as error:
		_handle_error(error)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
