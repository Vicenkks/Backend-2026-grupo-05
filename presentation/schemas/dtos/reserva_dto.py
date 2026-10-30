
from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict

from domain.reserva_domain import EstadoReserva


class ReservaCreateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    espacio_id: UUID
    empresa_id: UUID
    fecha_inicio: AwareDatetime
    fecha_fin: AwareDatetime


class ReservaResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    espacio_id: UUID
    empresa_id: UUID
    fecha_inicio: AwareDatetime
    fecha_fin: AwareDatetime
    estado: EstadoReserva


class ReservaPaginaDTO(BaseModel):
    items: list[ReservaResponseDTO]
    total: int
    pagina: int
    limite: int
    total_paginas: int
