from pydantic import BaseModel, Field
from enum import Enum

class SpaceStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class SpaceCreate(BaseModel):
    spaceName: str = Field(..., min_length=3, max_length=50)
    type: str = Field(..., min_length=2, description="Space type (e.g., meeting_room)")
    capacity: int = Field(..., gt=0, le=200, description="Capacity between 1 and 200")
    status: SpaceStatusEnum = SpaceStatusEnum.ACTIVE
    description: str = Field(..., max_length=200)

class SpaceUpdate(BaseModel):
    spaceName: str | None = Field(None, min_length=3, max_length=50)
    type: str | None = None
    capacity: int | None = Field(None, gt=0, le=200)
    status: SpaceStatusEnum | None = None
    description: str | None = Field(None, max_length=200)

class SpaceResponse(SpaceCreate):
    spaceId: str
    created_at: str
    updated_at: str