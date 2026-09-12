from app.domain.availability import Availability

class AvailabilityRepository:
    def __init__(self):
        self.availabilities : dict[str, Availability] = {}

    def add(self, availability: Availability) -> Availability:
        self.availabilities[availability.availabilityId] = availability
        return availability

    def get_by_id(self,availabilityId: str) -> Availability | None:
        return self.availabilities.get(availabilityId)

    def get_all(self) -> list[Availability]:
        return list(self.availabilities.values())

    def delete(self, availability: Availability) -> bool:
       return self.availabilities.pop(availability.availabilityId, None) is not None