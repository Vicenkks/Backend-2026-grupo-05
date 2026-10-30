
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.espacio_domain import TipoEspacio, EstadoEspacio


class EspacioCreateDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    nombre: str = Field(min_length=1, max_length=100)
    tipo: TipoEspacio
    capacidad: int = Field(ge=1)
    estado: EstadoEspacio = EstadoEspacio.ACTIVO


class EspacioUpdateDTO(EspacioCreateDTO):
    """Para actualizar se requieren los campos del espacio."""

    pass


class EspacioResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    tipo: TipoEspacio
    capacidad: int
    estado: EstadoEspacio


class EspacioPaginaDTO(BaseModel):
    items: list[EspacioResponseDTO]
    total: int
    pagina: int
    limite: int
    total_paginas: int
