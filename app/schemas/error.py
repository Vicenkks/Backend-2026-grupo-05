from pydantic import BaseModel
from typing import List, Optional

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    error: dict

    @classmethod
    def create(cls, code: str, message: str, details: List[dict] = None):
        return cls(
            error={
                "code": code,
                "message": message,
                "details": details or []
            }
        )