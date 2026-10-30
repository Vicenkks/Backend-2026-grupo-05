from application.services.espacio_service import EspacioService
from domain.espacio_domain import Espacio, TipoEspacio, EstadoEspacio


def seed_espacios(service: EspacioService) -> list[Espacio]:
    """Carga espacios de prueba."""
    espacios = [
        {
            "nombre": "Sala de reuniones A",
            "tipo": TipoEspacio.SALA_REUNION,
            "capacidad": 10,
            "estado": EstadoEspacio.ACTIVO,
        },
        {
            "nombre": "Sala de reuniones B",
            "tipo": TipoEspacio.SALA_REUNION,
            "capacidad": 6,
            "estado": EstadoEspacio.ACTIVO,
        },
        {
            "nombre": "Escritorio compartido 1",
            "tipo": TipoEspacio.ESCRITORIO,
            "capacidad": 1,
            "estado": EstadoEspacio.ACTIVO,
        },
        {
            "nombre": "Escritorio compartido 2",
            "tipo": TipoEspacio.ESCRITORIO,
            "capacidad": 1,
            "estado": EstadoEspacio.MANTENIMIENTO,
        },
        {
            "nombre": "Oficina privada 1",
            "tipo": TipoEspacio.OFICINA,
            "capacidad": 4,
            "estado": EstadoEspacio.ACTIVO,
        },
    ]

    creados = []

    for datos in espacios:
        espacio = service.crear(
            nombre=datos["nombre"],
            tipo=datos["tipo"],
            capacidad=datos["capacidad"],
            estado=datos["estado"],
        )
        creados.append(espacio)

    return creados
