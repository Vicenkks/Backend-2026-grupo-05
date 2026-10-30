
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)

from application.services.disponibilidad_service import DisponibilidadService
from presentation.dependencies import get_disponibilidad_service
from presentation.schemas.dtos.disponibilidad_dto import (
    DisponibilidadCreateDTO,
    DisponibilidadUpdateDTO,
    DisponibilidadResponseDTO,
    DisponibilidadPaginaDTO,
)
from presentation.schemas.dtos.disponibilidad_query_dto import (
    DisponibilidadQueryDTO,
)


router = APIRouter(
    prefix="/disponibilidades",
    tags=["Disponibilidades"],
)

ServiceDep = Annotated[
    DisponibilidadService,
    Depends(get_disponibilidad_service),
]
DisponibilidadId = Annotated[UUID, Path()]


@router.post(
    "",
    response_model=DisponibilidadResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def crear_disponibilidad(
    datos: DisponibilidadCreateDTO,
    service: ServiceDep,
):
    try:
        disponibilidad = service.crear(
            espacio_id=datos.espacio_id,
            dia_semana=datos.dia_semana,
            hora_apertura=datos.hora_apertura,
            hora_cierre=datos.hora_cierre,
            activa=datos.activa,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return DisponibilidadResponseDTO.model_validate(disponibilidad)


@router.get("", response_model=DisponibilidadPaginaDTO)
def listar_disponibilidades(
    query: Annotated[DisponibilidadQueryDTO, Query()],
    service: ServiceDep,
):
    disponibilidades, total = service.listar(
        pagina=query.pagina,
        tamano=query.tamano,
        espacio_id=query.espacio_id,
        dia_semana=query.dia_semana,
        activa=query.activa,
    )

    return DisponibilidadPaginaDTO(
        items=[
            DisponibilidadResponseDTO.model_validate(disponibilidad)
            for disponibilidad in disponibilidades
        ],
        total=total,
        pagina=query.pagina,
        limite=query.tamano,
        total_paginas=(total + query.tamano - 1) // query.tamano,
    )


@router.get(
    "/{disponibilidad_id}",
    response_model=DisponibilidadResponseDTO,
)
def obtener_disponibilidad(
    disponibilidad_id: DisponibilidadId,
    service: ServiceDep,
):
    disponibilidad = service.obtener(disponibilidad_id)

    if disponibilidad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La disponibilidad no existe.",
        )

    return DisponibilidadResponseDTO.model_validate(disponibilidad)


@router.put(
    "/{disponibilidad_id}",
    response_model=DisponibilidadResponseDTO,
)
def actualizar_disponibilidad(
    disponibilidad_id: DisponibilidadId,
    datos: DisponibilidadUpdateDTO,
    service: ServiceDep,
):
    try:
        disponibilidad = service.actualizar(
            disponibilidad_id=disponibilidad_id,
            espacio_id=datos.espacio_id,
            dia_semana=datos.dia_semana,
            hora_apertura=datos.hora_apertura,
            hora_cierre=datos.hora_cierre,
            activa=datos.activa,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if disponibilidad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La disponibilidad no existe.",
        )

    return DisponibilidadResponseDTO.model_validate(disponibilidad)


@router.delete(
    "/{disponibilidad_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_disponibilidad(
    disponibilidad_id: DisponibilidadId,
    service: ServiceDep,
):
    eliminada = service.eliminar(disponibilidad_id)

    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La disponibilidad no existe.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
