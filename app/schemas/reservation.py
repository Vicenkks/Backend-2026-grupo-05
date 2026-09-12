from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum

class ReservationStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"

class ReservationCreate(BaseModel):
    spaceId: str = Field(..., description="Space ID (must exist)")
    companyId: str = Field(..., description="Company ID (must exist)")
    start_date: datetime
    end_date: datetime
    reason: str = Field(..., min_length=5, max_length=200)
    status: ReservationStatusEnum = ReservationStatusEnum.PENDING

    @model_validator(mode='after')
    def validate_dates(self) -> 'ReservationCreate':
        if self.end_date <= self.start_date:
            raise ValueError("End date must be later than start date")
        return self

class ReservationUpdate(BaseModel):
    spaceId: str | None = None
    companyId: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    reason: str | None = Field(None, min_length=5, max_length=200)
    status: ReservationStatusEnum | None = None

class ReservationResponse(ReservationCreate):
    reservationId: str
    created_at: str
    updated_at: str