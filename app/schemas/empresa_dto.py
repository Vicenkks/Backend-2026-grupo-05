from pydantic import BaseModel, Field, EmailStr

class EmpresaCreate(BaseModel):
    nombreEmpresa: str = Field(..., min_length=3, max_length=100)

    rut: str = Field(..., pattern=r"^\d{7,8}-[\dkK]$", description="Formato: 12345678-9")
    
    email: EmailStr
    telefono: str = Field(..., min_length=8, max_length=15)
    direccion: str = Field(..., min_length=5, max_length=100)

class EmpresaUpdate(BaseModel):
    nombreEmpresa: str | None = Field(None, min_length=3, max_length=100)
    rut: str | None = Field(None, pattern=r"^\d{7,8}-[\dkK]$")
    email: EmailStr | None = None
    telefono: str | None = Field(None, min_length=8, max_length=15)
    direccion: str | None = Field(None, min_length=5, max_length=100)

class EmpresaResponse(EmpresaCreate):
    idEmpresa: str
    creado_en: str
    actualizado_en: str