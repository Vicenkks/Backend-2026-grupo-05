from pydantic import BaseModel, Field
from datetime import time
from enum import Enum

class DiaSemanaEnum(str, Enum):
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    DOMINGO = "domingo"

class DisponibilidadCreate(BaseModel):
    idEspacio: str = Field(..., description="ID del espacio")
    dia_semana: DiaSemanaEnum
    hora_apertura: time
    hora_cierre: time

class DisponibilidadUpdate(BaseModel):
    idEspacio: str | None = None
    dia_semana: DiaSemanaEnum | None = None
    hora_apertura: time | None = None
    hora_cierre: time | None = None

class DisponibilidadResponse(DisponibilidadCreate):
    idDisponibilidad: str
    creado_en: str
    actualizado_en: str