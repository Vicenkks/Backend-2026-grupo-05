from pydantic import BaseModel, Field

class Paginacion(BaseModel):
    pagina: int = Field(1, ge=1, description="Número de página (inicia en 1)")
    limite: int = Field(20, ge=1, le=100, description="Elementos por página (1 a 100)")
    ordenar_por: str = Field("creado_en", description="Campo a ordenar")
    direccion: str = Field("desc", pattern="^(asc|desc)$", description="Dirección (asc o desc)")