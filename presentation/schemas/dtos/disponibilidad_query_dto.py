
from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field


class DisponibilidadQueryDTO(BaseModel):
    pagina: int = Field(default=1, ge=1)
    limite: int = Field(default=10, ge=1, le=100, validation_alias=AliasChoices("limite", "tamano"))

    @property
    def tamano(self) -> int:
        return self.limite
    espacio_id: UUID | None = None
    dia_semana: int | None = Field(default=None, ge=0, le=6)
    activa: bool | None = None
