
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID


class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"


@dataclass
class Reserva:
    id: UUID
    espacio_id: UUID
    empresa_id: UUID
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: EstadoReserva = EstadoReserva.CONFIRMADA

    def __post_init__(self):
        if self.fecha_inicio.tzinfo is None:
            raise ValueError(
                "La fecha de inicio debe incluir zona horaria"
            )

        if self.fecha_fin.tzinfo is None:
            raise ValueError(
                "La fecha de fin debe incluir zona horaria"
            )

        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError(
                "La fecha de fin debe ser posterior al inicio"
            )

        if self.fecha_fin - self.fecha_inicio < timedelta(minutes=30):
            raise ValueError(
                "La duración mínima de una reserva es de 30 minutos"
            )

    def se_superpone_con(self, otra: "Reserva") -> bool:
        return (
            self.fecha_inicio < otra.fecha_fin
            and otra.fecha_inicio < self.fecha_fin
        )

    def ocupa_espacio(self) -> bool:
        return self.estado in {
            EstadoReserva.PENDIENTE,
            EstadoReserva.CONFIRMADA,
        }

    def cancelar(self, ahora: datetime | None = None):
        if self.estado == EstadoReserva.CANCELADA:
            raise ValueError("La reserva ya está cancelada")

        if ahora is None:
            ahora = datetime.now(self.fecha_inicio.tzinfo)

        if ahora.tzinfo is None:
            raise ValueError("La fecha actual debe incluir zona horaria")

        if ahora >= self.fecha_inicio:
            raise ValueError(
                "No se puede cancelar una reserva que ya comenzó"
            )

        self.estado = EstadoReserva.CANCELADA
