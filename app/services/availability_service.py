from datetime import datetime

from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.space_repository import SpaceRepository
from app.domain.availability import Availability
from app.domain.availability import Weekday
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate

class AvailabilityService:
    def __init__(self, availability_repository: AvailabilityRepository, space_repository: SpaceRepository) -> None:
        self.availability_repository = availability_repository
        self.space_repository = space_repository

    def create(self, data: AvailabilityCreate) -> Availability:
        self._ensure_space_exists(data.spaceId)
        availability = Availability.create(
            spaceId=data.spaceId,
            weekday=Weekday(data.weekday.value),
            opening_time=data.opening_time,
            closing_time=data.closing_time,
        )
        return self.availability_repository.add(availability)

    def get_by_id(self, availability_id: str) -> Availability:
        availability = self.availability_repository.get_by_id(availability_id)
        if availability is None:
            raise LookupError(f"Availability '{availability_id}' was not found")
        return availability

    def get_all(self) -> list[Availability]:
        return self.availability_repository.get_all()

    def update(self, availability_id: str, data: AvailabilityUpdate) -> Availability:
        availability = self.get_by_id(availability_id)
        if data.spaceId is not None:
            self._ensure_space_exists(data.spaceId)
            availability.spaceId = data.spaceId.strip()
        if data.weekday is not None:
            availability.weekday = Weekday(data.weekday.value)
        if data.opening_time is not None or data.closing_time is not None:
            availability.update_schedule(data.opening_time, data.closing_time)
        else:
            availability.updated_at = datetime.now()
        return availability

    def delete(self, availability_id: str) -> None:
        availability = self.get_by_id(availability_id)
        if not self.availability_repository.delete(availability):
            raise LookupError(f"Availability '{availability_id}' was not found")

    def _ensure_space_exists(self, space_id: str) -> None:
        if self.space_repository.get_by_id(space_id) is None:
            raise LookupError(f"Space '{space_id}' was not found")

