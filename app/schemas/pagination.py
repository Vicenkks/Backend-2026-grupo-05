from pydantic import BaseModel, Field

class Pagination(BaseModel):
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    limit: int = Field(20, ge=1, le=100, description="Items per page (1 to 100)")
    sort_by: str = Field("created_at", description="Field to sort by")
    direction: str = Field("desc", pattern="^(asc|desc)$", description="Direction (asc or desc)")