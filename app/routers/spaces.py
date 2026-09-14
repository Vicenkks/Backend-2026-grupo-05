from math import ceil

from fastapi import APIRouter, HTTPException, Response, status

from app.repositories.instances import availability_repository, reservation_repository, space_repository
from app.schemas.space import SpaceCreate, SpaceResponse, SpaceUpdate
from app.services.space_service import SpaceService

router = APIRouter(prefix="/spaces", tags=["Spaces"], responses={400: {"description": "Business rule error"}, 404: {"description": "Space not found"}, 409: {"description": "Related records conflict"}, 422: {"description": "Invalid data"}})
service = SpaceService(space_repository, reservation_repository, availability_repository)


def _serialize(space):
	return {
		"spaceId": space.spaceId,
		"spaceName": space.spaceName,
		"type": space.type,
		"capacity": space.capacity,
		"status": space.status.value,
		"description": space.description,
		"created_at": space.created_at.isoformat(),
		"updated_at": space.updated_at.isoformat(),
	}


def _handle_error(error: Exception) -> None:
	if isinstance(error, LookupError):
		raise HTTPException(status_code=404, detail={"code": "RESOURCE_NOT_FOUND", "message": str(error), "details": []}) from error
	if "Cannot delete" in str(error):
		raise HTTPException(status_code=409, detail={"code": "CONFLICT", "message": str(error), "details": []}) from error
	raise HTTPException(status_code=400, detail={"code": "BUSINESS_RULE_VIOLATION", "message": str(error), "details": []}) from error


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SpaceResponse)
def create_space(data: SpaceCreate):
	"""Create a new coworking space."""
	try:
		return _serialize(service.create(data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.get("")
def list_spaces(page: int = 1, limit: int = 20, sort_by: str = "created_at", direction: str = "desc", type: str | None = None, status: str | None = None, min_capacity: int | None = None):
	"""List spaces using filters, sorting and pagination."""
	if page < 1 or not 1 <= limit <= 100 or direction not in {"asc", "desc"}:
		raise HTTPException(status_code=422, detail="Invalid pagination parameters")
	if status is not None and status not in {"active", "inactive", "maintenance"}:
		raise HTTPException(status_code=422, detail="Invalid status")
	if min_capacity is not None and min_capacity < 1:
		raise HTTPException(status_code=422, detail="Invalid minimum capacity")
	if sort_by not in {"spaceName", "type", "capacity", "status", "created_at", "updated_at"}:
		raise HTTPException(status_code=422, detail="Invalid sort field")
	spaces = service.get_all()
	if type is not None:
		spaces = [space for space in spaces if space.type == type]
	if status is not None:
		spaces = [space for space in spaces if space.status.value == status]
	if min_capacity is not None:
		spaces = [space for space in spaces if space.capacity >= min_capacity]
	spaces.sort(key=lambda space: getattr(space, sort_by), reverse=direction == "desc")
	total = len(spaces)
	start = (page - 1) * limit
	return {"items": [_serialize(space) for space in spaces[start:start + limit]], "total": total, "page": page, "limit": limit, "total_pages": ceil(total / limit) if total else 0}


@router.get("/{space_id}", response_model=SpaceResponse)
def get_space(space_id: str):
	"""Get one space by its ID."""
	try:
		return _serialize(service.get_by_id(space_id))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.put("/{space_id}", response_model=SpaceResponse)
def update_space(space_id: str, data: SpaceUpdate):
	"""Update an existing space."""
	try:
		return _serialize(service.update(space_id, data))
	except (LookupError, ValueError) as error:
		_handle_error(error)


@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space(space_id: str) -> Response:
	"""Delete a space when it has no related records."""
	try:
		service.delete(space_id)
	except (LookupError, ValueError) as error:
		_handle_error(error)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
