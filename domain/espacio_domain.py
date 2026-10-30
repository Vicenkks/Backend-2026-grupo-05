
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class TipoEspacio(str, Enum):
    SALA_REUNION = "sala_reunion"
    ESCRITORIO = "escritorio"
    OFICINA = "oficina"


class EstadoEspacio(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"


@dataclass
class Espacio:
    id: UUID
    nombre: str
    tipo: TipoEspacio
    capacidad: int
    estado: EstadoEspacio = EstadoEspacio.ACTIVO

    def __post_init__(self):
        if not self.nombre.strip():
            raise ValueError("El nombre es obligatorio")

        if self.capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que cero")

    def cambiar_estado(self, nuevo_estado: EstadoEspacio):
        self.estado = nuevo_estado

    def esta_disponible_para_reserva(self) -> bool:
        return self.estado == EstadoEspacio.ACTIVO
