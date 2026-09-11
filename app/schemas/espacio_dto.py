from pydantic import BaseModel, Field
from enum import Enum

class EstadoEspacioEnum(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"

class EspacioCreate(BaseModel):
    nombreEspacio: str = Field(..., min_length=3, max_length=50)
    tipo: str = Field(..., min_length=2, description="Tipo de espacio (ej: sala_reunion)")
    
    capacidad: int = Field(..., gt=0, le=200, description="Capacidad entre 1 y 200")
    
    estado: EstadoEspacioEnum = EstadoEspacioEnum.ACTIVO
    descripcion: str = Field(..., max_length=200)

class EspacioUpdate(BaseModel):
    nombreEspacio: str | None = Field(None, min_length=3, max_length=50)
    tipo: str | None = None
    capacidad: int | None = Field(None, gt=0, le=200)
    estado: EstadoEspacioEnum | None = None
    descripcion: str | None = Field(None, max_length=200)

class EspacioResponse(EspacioCreate):
    idEspacio: str
    creado_en: str
    actualizado_en: str