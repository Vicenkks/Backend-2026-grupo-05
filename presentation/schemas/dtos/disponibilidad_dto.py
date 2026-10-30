
from datetime import time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DisponibilidadCreateDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    espacio_id: UUID
    dia_semana: int = Field(ge=0, le=6)
    hora_apertura: time
    hora_cierre: time
    activa: bool = True


class DisponibilidadUpdateDTO(DisponibilidadCreateDTO):
    """Para actualizar se requieren los campos de disponibilidad."""

    pass


class DisponibilidadResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    espacio_id: UUID
    dia_semana: int
    hora_apertura: time
    hora_cierre: time
    activa: bool


class DisponibilidadPaginaDTO(BaseModel):
    items: list[DisponibilidadResponseDTO]
    total: int
    pagina: int
    limite: int
    total_paginas: int
