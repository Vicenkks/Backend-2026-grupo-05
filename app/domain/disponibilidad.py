from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from uuid import uuid4


class DiaSemana(str, Enum):
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    DOMINGO = "domingo"

@dataclass
class Disponibilidad:
    idDisponibilidad: str
    idEspacio: str
    dia_semana: DiaSemana
    hora_apertura: time
    hora_cierre: time
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def crear(cls, idEspacio: str, dia_semana: DiaSemana, hora_apertura: time, hora_cierre: time) -> "Disponibilidad":
        if hora_cierre <= hora_apertura:
            raise ValueError("La hora de cierre debe ser posterior a la hora de apertura")

        ahora = datetime.now()
        return cls(
            idDisponibilidad=str(uuid4()),
            idEspacio=idEspacio.strip(),
            dia_semana=dia_semana,
            hora_apertura=hora_apertura,
            hora_cierre=hora_cierre,
            creado_en=ahora,
            actualizado_en=ahora
        )

    def actualizar_horario(self, hora_apertura: time = None, hora_cierre: time = None):
        if hora_apertura is not None:
            self.hora_apertura = hora_apertura
        if hora_cierre is not None:
            self.hora_cierre = hora_cierre
        if self.hora_cierre <= self.hora_apertura:
            raise ValueError("La hora de cierre debe ser posterior a la hora de apertura")
        self.actualizado_en = datetime.now()