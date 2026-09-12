from app.domain.availability import Availability
#Obs: So basically, we will use dictionary as db,
# our crud will be like:
# add -> dict[IdofSomething] = value
# get_by_id -> dict.get(IdofSomething)
# get_all -> list(dict.values())
# delete -> dict.pop(IdofSomething, None)

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