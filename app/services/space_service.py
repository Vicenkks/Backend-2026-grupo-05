from app.domain.space import Space, SpaceStatus
from app.repositories.space_repository import SpaceRepository
from app.schemas.space import SpaceCreate, SpaceUpdate


class SpaceService:
	def __init__(self, space_repository: SpaceRepository, reservation_repository=None, availability_repository=None) -> None:
		self.space_repository = space_repository
		self.reservation_repository = reservation_repository
		self.availability_repository = availability_repository

	def create(self, data: SpaceCreate) -> Space:
		space = Space.create(
			spaceName=data.spaceName,
			type=data.type,
			capacity=data.capacity,
			description=data.description,
			status=SpaceStatus(data.status.value),
		)
		return self.space_repository.add(space)

	def get_by_id(self, space_id: str) -> Space:
		space = self.space_repository.get_by_id(space_id)
		if space is None:
			raise LookupError(f"Space '{space_id}' was not found")
		return space

	def get_all(self) -> list[Space]:
		return self.space_repository.get_all()

	def update(self, space_id: str, data: SpaceUpdate) -> Space:
		space = self.get_by_id(space_id)
		space.update(
			spaceName=data.spaceName,
			type=data.type,
			capacity=data.capacity,
			status=SpaceStatus(data.status.value) if data.status is not None else None,
			description=data.description,
		)
		return space

	def delete(self, space_id: str) -> None:
		space = self.get_by_id(space_id)
		if self.reservation_repository is not None:
			for reservation in self.reservation_repository.get_all():
				if reservation.spaceId == space_id:
					raise ValueError("Cannot delete a space with reservations")
		if self.availability_repository is not None:
			for availability in self.availability_repository.get_all():
				if availability.spaceId == space_id:
					raise ValueError("Cannot delete a space with availabilities")
		if not self.space_repository.delete(space):
			raise LookupError(f"Space '{space_id}' was not found")
