
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)

from application.services.reserva_service import ReservaService
from presentation.dependencies import get_reserva_service
from presentation.schemas.dtos.reserva_dto import (
    ReservaCreateDTO,
    ReservaResponseDTO,
    ReservaPaginaDTO,
)
from presentation.schemas.dtos.reserva_query_dto import ReservaQueryDTO


router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"],
)

ServiceDep = Annotated[ReservaService, Depends(get_reserva_service)]
ReservaId = Annotated[UUID, Path()]


@router.post(
    "",
    response_model=ReservaResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def crear_reserva(datos: ReservaCreateDTO, service: ServiceDep):
    try:
        reserva = service.crear(
            espacio_id=datos.espacio_id,
            empresa_id=datos.empresa_id,
            fecha_inicio=datos.fecha_inicio,
            fecha_fin=datos.fecha_fin,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return ReservaResponseDTO.model_validate(reserva)


@router.get("", response_model=ReservaPaginaDTO)
def listar_reservas(
    query: Annotated[ReservaQueryDTO, Query()],
    service: ServiceDep,
):
    reservas, total = service.listar(
        pagina=query.pagina,
        tamano=query.tamano,
        espacio_id=query.espacio_id,
        empresa_id=query.empresa_id,
        estado=query.estado.value if query.estado else None,
        desde=query.desde,
        hasta=query.hasta,
    )

    return ReservaPaginaDTO(
        items=[
            ReservaResponseDTO.model_validate(reserva)
            for reserva in reservas
        ],
        total=total,
        pagina=query.pagina,
        limite=query.tamano,
        total_paginas=(total + query.tamano - 1) // query.tamano,
    )


@router.get(
    "/{reserva_id}",
    response_model=ReservaResponseDTO,
)
def obtener_reserva(reserva_id: ReservaId, service: ServiceDep):
    reserva = service.obtener(reserva_id)

    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La reserva no existe.",
        )

    return ReservaResponseDTO.model_validate(reserva)


@router.post(
    "/{reserva_id}/cancelar",
    response_model=ReservaResponseDTO,
)
def cancelar_reserva(reserva_id: ReservaId, service: ServiceDep):
    try:
        reserva = service.cancelar(reserva_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La reserva no existe.",
        )

    return ReservaResponseDTO.model_validate(reserva)
