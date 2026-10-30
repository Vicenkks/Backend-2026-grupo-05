from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmpresaCreateDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    nombre: str = Field(min_length=1, max_length=150)
    rut: str = Field(min_length=8, max_length=12)
    contacto: str = Field(min_length=1, max_length=150)
    activa: bool = True


class EmpresaUpdateDTO(EmpresaCreateDTO):
    """Para actualizar se requieren los campos de la empresa."""

    pass


class EmpresaResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    rut: str
    contacto: str
    activa: bool


class EmpresaPaginaDTO(BaseModel):
    items: list[EmpresaResponseDTO]
    total: int
    pagina: int
    limite: int
    total_paginas: int
