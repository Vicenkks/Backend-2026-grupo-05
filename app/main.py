
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from presentation.errors import register_error_handlers
from presentation.openapi import configure_openapi

from infrastructure.database import SessionLocal

from infrastructure.repositories.espacio_repository import EspacioRepository
from infrastructure.repositories.empresa_repository import EmpresaRepository
from infrastructure.repositories.disponibilidad_repository import DisponibilidadRepository
from infrastructure.repositories.reserva_repository import ReservaRepository

from application.services.espacio_service import EspacioService
from application.services.empresa_service import EmpresaService
from application.services.disponibilidad_service import DisponibilidadService
from application.services.reserva_service import ReservaService

from infrastructure.seeders.espacio_seeder import seed_espacios
from infrastructure.seeders.empresa_seeder import seed_empresas
from infrastructure.seeders.disponibilidad_seeder import seed_disponibilidades
from infrastructure.seeders.reserva_seeder import seed_reservas

from presentation.routers.espacio_router import router as espacio_router
from presentation.routers.empresa_router import router as empresa_router
from presentation.routers.disponibilidad_router import (
    router as disponibilidad_router,
)
from presentation.routers.reserva_router import router as reserva_router


def cargar_datos_iniciales() -> None:
    with SessionLocal.begin() as session:
        espacio_repository = EspacioRepository(session)
        empresa_repository = EmpresaRepository(session)
        disponibilidad_repository = DisponibilidadRepository(session)
        reserva_repository = ReservaRepository(session)
        espacios = espacio_repository.listar(limite=100)
        if not espacios:
            espacios = seed_espacios(EspacioService(espacio_repository))
        empresas = empresa_repository.listar(limite=100)
        if not empresas:
            empresas = seed_empresas(EmpresaService(empresa_repository))
        if disponibilidad_repository.contar() == 0:
            seed_disponibilidades(
                DisponibilidadService(disponibilidad_repository, espacio_repository), espacios
            )
        if reserva_repository.contar() == 0:
            seed_reservas(
                ReservaService(reserva_repository, espacio_repository,
                               empresa_repository, disponibilidad_repository),
                espacios, empresas,
            )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Las tablas las crea Alembic:
    # uv run alembic upgrade head
    cargar_datos_iniciales()
    yield


app = FastAPI(
    title="Sistema de Reservas de Coworking",
    lifespan=lifespan,
)

app.include_router(espacio_router)
app.include_router(empresa_router)
app.include_router(disponibilidad_router)
app.include_router(reserva_router)


register_error_handlers(app)
configure_openapi(app)
