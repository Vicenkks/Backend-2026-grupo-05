
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field

from domain.espacio_domain import TipoEspacio, EstadoEspacio


class EspacioQueryDTO(BaseModel):
    pagina: int = Field(default=1, ge=1)
    limite: int = Field(default=10, ge=1, le=100, validation_alias=AliasChoices("limite", "tamano"))

    @property
    def tamano(self) -> int:
        return self.limite
    ordenar_por: Literal["nombre", "capacidad", "tipo", "estado"] = "nombre"
    direccion: Literal["asc", "desc"] = "asc"
    tipo: TipoEspacio | None = None
    estado: EstadoEspacio | None = None
