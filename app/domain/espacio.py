from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4
from app.domain.validadores import validar_texto


class EstadoEspacio(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"

@dataclass
class Espacio:
    idEspacio: str
    nombreEspacio: str
    tipo: str
    capacidad: int
    estado: EstadoEspacio
    descripcion: str
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def crear(cls, nombreEspacio: str, tipo: str, capacidad: int, descripcion: str, estado: EstadoEspacio = EstadoEspacio.ACTIVO) -> "Espacio":
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor a cero")

        ahora = datetime.now()
        return cls(
            idEspacio=str(uuid4()),
            nombreEspacio=validar_texto(nombreEspacio, "nombre del espacio"),
            tipo=tipo.strip().lower(),
            capacidad=capacidad,
            estado=estado,
            descripcion=validar_texto(descripcion, "descripción"),
            creado_en=ahora,
            actualizado_en=ahora
        )

    def actualizar(self, nombreEspacio: str = None, tipo: str = None, capacidad: int = None, estado: EstadoEspacio = None, descripcion: str = None):
        if nombreEspacio is not None:
            self.nombreEspacio = validar_texto(nombreEspacio, "nombre del espacio")
        if tipo is not None:
            self.tipo = tipo.strip().lower()
        if capacidad is not None:
            if capacidad <= 0:
                raise ValueError("La capacidad debe ser mayor a cero")
            self.capacidad = capacidad
        if estado is not None:
            self.estado = estado
        if descripcion is not None:
            self.descripcion = validar_texto(descripcion, "descripción")
        self.actualizado_en = datetime.now()