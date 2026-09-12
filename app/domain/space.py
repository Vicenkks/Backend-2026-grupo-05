from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4
from app.domain.validators import validate_text

class SpaceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

@dataclass
class Space:
    spaceId: str
    spaceName: str
    type: str
    capacity: int
    status: SpaceStatus
    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, spaceName: str, type: str, capacity: int, description: str, status: SpaceStatus = SpaceStatus.ACTIVE) -> "Space":
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")
        now = datetime.now()
        return cls(
            spaceId=str(uuid4()),
            spaceName=validate_text(spaceName, "space name"),
            type=type.strip().lower(),
            capacity=capacity,
            status=status,
            description=validate_text(description, "description"),
            created_at=now,
            updated_at=now
        )

    def update(self, spaceName: str = None, type: str = None, capacity: int = None, status: SpaceStatus = None, description: str = None):
        if spaceName is not None:
            self.spaceName = validate_text(spaceName, "space name")
        if type is not None:
            self.type = type.strip().lower()
        if capacity is not None:
            if capacity <= 0:
                raise ValueError("Capacity must be greater than zero")
            self.capacity = capacity
        if status is not None:
            self.status = status
        if description is not None:
            self.description = validate_text(description, "description")
        self.updated_at = datetime.now()