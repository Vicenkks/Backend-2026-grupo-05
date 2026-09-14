from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from uuid import uuid4

class Weekday(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

@dataclass
class Availability:
    availabilityId: str
    spaceId: str
    weekday: Weekday
    opening_time: time
    closing_time: time
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, spaceId: str, weekday: Weekday, opening_time: time, closing_time: time) -> "Availability":
        if closing_time <= opening_time:
            raise ValueError("Closing time must be later than opening time")
        now = datetime.now()
        return cls(
            availabilityId=str(uuid4()),
            spaceId=spaceId.strip(),
            weekday=weekday,
            opening_time=opening_time,
            closing_time=closing_time,
            created_at=now,
            updated_at=now
        )

    def update_schedule(self, opening_time: time = None, closing_time: time = None):
        new_opening = self.opening_time
        new_closing = self.closing_time

        if opening_time is not None:
            new_opening = opening_time
        if closing_time is not None:
            new_closing = closing_time

        if new_closing <= new_opening:
            raise ValueError("Closing time must be later than opening time")

        self.opening_time = new_opening
        self.closing_time = new_closing
        self.updated_at = datetime.now()
