from pydantic import BaseModel, Field
from typing import Optional

class SpaceFilter(BaseModel):
    type: Optional[str] = Field(None, description="Filter by space type")
    status: Optional[str] = Field(None, description="Filter by status")
    min_capacity: Optional[int] = Field(None, ge=1, description="Minimum capacity")

class ReservationFilter(BaseModel):
    company_id: Optional[str] = Field(None, description="Filter by company")
    status: Optional[str] = Field(None, description="Filter by reservation status")