from dataclasses import dataclass
from uuid import UUID
from datetime import date, datetime, time


@dataclass(frozen=True)
class Disponibilidad:
    id: UUID
    espacio_id: UUID
    dia_semana: int  # Lunes = 0, domingo = 6
    hora_apertura: time
    hora_cierre: time
    activa: bool = True

    def __post_init__(self):
        if not 0 <= self.dia_semana <= 6:
            raise ValueError("El día de la semana no es válido")

        if self.hora_apertura >= self.hora_cierre:
            raise ValueError(
                "La apertura debe ser anterior al cierre"
            )

    def contiene(self, inicio: datetime, fin: datetime) -> bool:
        if not self.activa:
            return False

        if inicio.date() != fin.date():
            return False

        if inicio.weekday() != self.dia_semana:
            return False

        return (
            self.hora_apertura <= inicio.time()
            and fin.time() <= self.hora_cierre
        )
