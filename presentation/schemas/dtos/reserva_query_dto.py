
from datetime import datetime
from uuid import UUID

from pydantic import AliasChoices, AwareDatetime, BaseModel, Field

from domain.reserva_domain import EstadoReserva


class ReservaQueryDTO(BaseModel):
    pagina: int = Field(default=1, ge=1)
    limite: int = Field(default=10, ge=1, le=100, validation_alias=AliasChoices("limite", "tamano"))

    @property
    def tamano(self) -> int:
        return self.limite
    espacio_id: UUID | None = None
    empresa_id: UUID | None = None
    estado: EstadoReserva | None = None
    desde: AwareDatetime | None = None
    hasta: AwareDatetime | None = None
