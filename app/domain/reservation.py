from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4
from app.domain.validators import validate_text

class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"

@dataclass
class Reservation:
    reservationId: str
    spaceId: str
    companyId: str
    start_date: datetime
    end_date: datetime
    status: ReservationStatus
    reason: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, spaceId: str, companyId: str, start_date: datetime, end_date: datetime, reason: str, status: ReservationStatus = ReservationStatus.PENDING) -> "Reservation":
        if end_date <= start_date:
            raise ValueError("End date must be later than start date")
        duration = (end_date - start_date).total_seconds() / 60
        if duration < 30:
            raise ValueError("Minimum duration must be 30 minutes")
        now = datetime.now()
        return cls(
            reservationId=str(uuid4()),
            spaceId=spaceId.strip(),
            companyId=companyId.strip(),
            start_date=start_date,
            end_date=end_date,
            status=status,
            reason=validate_text(reason, "reason"),
            created_at=now,
            updated_at=now
        )

    def cancel(self):
        if self.status == ReservationStatus.CANCELED:
            raise ValueError("Reservation is already canceled")
        if self.status == ReservationStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed reservation")
        self.status = ReservationStatus.CANCELED
        self.updated_at = datetime.now()

    def confirm(self):
        if self.status != ReservationStatus.PENDING:
            raise ValueError("Only pending reservations can be confirmed")
        self.status = ReservationStatus.CONFIRMED
        self.updated_at = datetime.now()