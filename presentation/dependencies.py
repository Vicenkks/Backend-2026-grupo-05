from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.database import SessionLocal

from infrastructure.repositories.espacio_repository import EspacioRepository
from infrastructure.repositories.empresa_repository import EmpresaRepository
from infrastructure.repositories.disponibilidad_repository import DisponibilidadRepository
from infrastructure.repositories.reserva_repository import ReservaRepository

from application.services.espacio_service import EspacioService
from application.services.empresa_service import EmpresaService
from application.services.disponibilidad_service import DisponibilidadService
from application.services.reserva_service import ReservaService


def get_session() -> Iterator[Session]:
    """Abre una sesión por solicitud y la cierra al terminar."""
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session, scope="function")]


def get_espacio_service(session: SessionDep) -> EspacioService:
    return EspacioService(
        EspacioRepository(session),
    )


def get_empresa_service(session: SessionDep) -> EmpresaService:
    return EmpresaService(
        EmpresaRepository(session),
    )


def get_disponibilidad_service(session: SessionDep) -> DisponibilidadService:
    return DisponibilidadService(
        DisponibilidadRepository(session),
        EspacioRepository(session),
    )


def get_reserva_service(session: SessionDep) -> ReservaService:
    return ReservaService(
        ReservaRepository(session),
        EspacioRepository(session),
        EmpresaRepository(session),
        DisponibilidadRepository(session),
    )
