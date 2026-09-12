from pydantic import BaseModel, Field
from datetime import time
from enum import Enum

class WeekdayEnum(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class AvailabilityCreate(BaseModel):
    spaceId: str = Field(..., description="Space ID")
    weekday: WeekdayEnum
    opening_time: time
    closing_time: time

class AvailabilityUpdate(BaseModel):
    spaceId: str | None = None
    weekday: WeekdayEnum | None = None
    opening_time: time | None = None
    closing_time: time | None = None

class AvailabilityResponse(AvailabilityCreate):
    availabilityId: str
    created_at: str
    updated_at: str