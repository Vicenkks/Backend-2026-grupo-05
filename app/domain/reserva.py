from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4
from app.domain.validadores import validar_texto


class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"

@dataclass
class Reserva:
    idReserva: str
    idEspacio: str
    idEmpresa: str
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: EstadoReserva
    motivo: str
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def crear(cls, idEspacio: str, idEmpresa: str, fecha_inicio: datetime, fecha_fin: datetime, motivo: str, estado: EstadoReserva = EstadoReserva.PENDIENTE) -> "Reserva":
        if fecha_fin <= fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")

        duracion = (fecha_fin - fecha_inicio).total_seconds() / 60
        if duracion < 30:
            raise ValueError("La duración mínima debe ser de 30 minutos")

        ahora = datetime.now()
        return cls(
            idReserva=str(uuid4()),
            idEspacio=idEspacio.strip(),
            idEmpresa=idEmpresa.strip(),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=estado,
            motivo=validar_texto(motivo, "motivo"),
            creado_en=ahora,
            actualizado_en=ahora
        )

    def cancelar(self):
        if self.estado == EstadoReserva.CANCELADA:
            raise ValueError("La reserva ya está cancelada")
        if self.estado == EstadoReserva.COMPLETADA:
            raise ValueError("No se puede cancelar una reserva completada")
        self.estado = EstadoReserva.CANCELADA
        self.actualizado_en = datetime.now()

    def confirmar(self):
        if self.estado != EstadoReserva.PENDIENTE:
            raise ValueError("Solo se pueden confirmar reservas pendientes")
        self.estado = EstadoReserva.CONFIRMADA
        self.actualizado_en = datetime.now()