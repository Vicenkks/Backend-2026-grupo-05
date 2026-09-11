from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum

class EstadoReservaEnum(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"

class ReservaCreate(BaseModel):
    idEspacio: str = Field(..., description="ID del espacio (debe existir)")
    idEmpresa: str = Field(..., description="ID de la empresa (debe existir)")
    
    fecha_inicio: datetime
    fecha_fin: datetime
    motivo: str = Field(..., min_length=5, max_length=200)
    estado: EstadoReservaEnum = EstadoReservaEnum.PENDIENTE

    @model_validator(mode='after')
    def validar_fechas(self) -> 'ReservaCreate':
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        return self

class ReservaUpdate(BaseModel):
    idEspacio: str | None = None
    idEmpresa: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    motivo: str | None = Field(None, min_length=5, max_length=200)
    estado: EstadoReservaEnum | None = None

class ReservaResponse(ReservaCreate):
    idReserva: str
    creado_en: str
    actualizado_en: str