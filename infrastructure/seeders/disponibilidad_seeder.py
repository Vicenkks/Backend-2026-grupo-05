from datetime import time

from application.services.disponibilidad_service import DisponibilidadService
from domain.espacio_domain import Espacio


def seed_disponibilidades(
    service: DisponibilidadService,
    espacios: list[Espacio],
) -> None:
    """Carga horarios de atención para los espacios activos."""

    for espacio in espacios:
        if espacio.estado.value != "activo":
            continue

        for dia in range(5):  # Lunes a viernes
            service.crear(
                espacio_id=espacio.id,
                dia_semana=dia,
                hora_apertura=time(9, 0),
                hora_cierre=time(18, 0),
                activa=True,
            )
