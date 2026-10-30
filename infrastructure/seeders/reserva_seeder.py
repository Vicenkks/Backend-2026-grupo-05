from datetime import datetime, timedelta, timezone
from domain.espacio_domain import Espacio, EstadoEspacio
from domain.empresa_domain import Empresa
from domain.reserva_domain import Reserva
from application.services.reserva_service import ReservaService


def seed_reservas(service: ReservaService, espacios: list[Espacio], empresas: list[Empresa]) -> list[Reserva]:
    """Carga reservas de prueba."""
    espacios_activos = [espacio for espacio in espacios if espacio.estado == EstadoEspacio.ACTIVO]
    empresas_activas = [empresa for empresa in empresas if empresa.activa]

    if not espacios_activos or not empresas_activas:
        return []

    reservas = []
    fecha = datetime.now(timezone.utc) + timedelta(days=1)

    # Buscar el siguiente día laborable.
    while fecha.weekday() >= 5:
        fecha += timedelta(days=1)

    fecha_inicio = fecha.replace(hour=10, minute=0, second=0, microsecond=0)

    for desplazamiento in range(2):
        inicio = fecha_inicio + timedelta(hours=desplazamiento)
        reservas.append(service.crear(
            espacio_id=espacios_activos[0].id,
            empresa_id=empresas_activas[0].id,
            fecha_inicio=inicio,
            fecha_fin=inicio + timedelta(hours=1),
        ))
    return reservas
