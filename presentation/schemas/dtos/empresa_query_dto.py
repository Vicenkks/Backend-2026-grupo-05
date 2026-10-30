
from pydantic import AliasChoices, BaseModel, Field


class EmpresaQueryDTO(BaseModel):
    pagina: int = Field(default=1, ge=1)
    limite: int = Field(default=10, ge=1, le=100, validation_alias=AliasChoices("limite", "tamano"))

    @property
    def tamano(self) -> int:
        return self.limite
    activa: bool | None = None
