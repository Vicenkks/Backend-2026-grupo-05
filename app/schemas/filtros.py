from pydantic import BaseModel, Field
from typing import Optional

class FiltroEspacio(BaseModel):
    tipo: Optional[str] = Field(None, description="Filtrar por tipo de espacio")
    estado: Optional[str] = Field(None, description="Filtrar por estado")
    capacidad_min: Optional[int] = Field(None, ge=1, description="Capacidad mínima")

class FiltroReserva(BaseModel):
    id_empresa: Optional[str] = Field(None, description="Filtrar por empresa")
    estado: Optional[str] = Field(None, description="Filtrar por estado de reserva")