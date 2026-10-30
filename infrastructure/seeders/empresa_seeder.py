from application.services.empresa_service import EmpresaService
from domain.empresa_domain import Empresa


def seed_empresas(service: EmpresaService) -> list[Empresa]:
    """Carga empresas de prueba."""
    empresas = [
        {
            "nombre": "Empresa Uno",
            "rut": "76123456-0",
            "contacto": "contacto@empresauno.cl",
            "activa": True,
        },
        {
            "nombre": "Empresa Dos",
            "rut": "77456789-5",
            "contacto": "contacto@empresados.cl",
            "activa": True,
        },
        {
            "nombre": "Empresa Tres",
            "rut": "76543210-3",
            "contacto": "contacto@empresatres.cl",
            "activa": False,
        },
    ]

    creadas = []

    for datos in empresas:
        empresa = service.crear(
            nombre=datos["nombre"],
            rut=datos["rut"],
            contacto=datos["contacto"],
            activa=datos["activa"],
        )
        creadas.append(empresa)

    return creadas
