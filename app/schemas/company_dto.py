from pydantic import BaseModel, Field, EmailStr

class CompanyCreate(BaseModel):
    companyName: str = Field(..., min_length=3, max_length=100)
    rut: str = Field(..., pattern=r"^\d{7,8}-[\dkK]$", description="Format: 12345678-9")
    email: EmailStr
    phone: str = Field(..., min_length=8, max_length=15)
    address: str = Field(..., min_length=5, max_length=100)

class CompanyUpdate(BaseModel):
    companyName: str | None = Field(None, min_length=3, max_length=100)
    rut: str | None = Field(None, pattern=r"^\d{7,8}-[\dkK]$")
    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=8, max_length=15)
    address: str | None = Field(None, min_length=5, max_length=100)

class CompanyResponse(CompanyCreate):
    companyId: str
    created_at: str
    updated_at: str
