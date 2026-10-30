
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

from application.services.espacio_service import EspacioService
from presentation.dependencies import get_espacio_service
from presentation.schemas.dtos.espacio_dto import (
    EspacioCreateDTO,
    EspacioUpdateDTO,
    EspacioResponseDTO,
    EspacioPaginaDTO,
)
from presentation.schemas.dtos.espacio_query_dto import EspacioQueryDTO


router = APIRouter(
    prefix="/espacios",
    tags=["Espacios"],
)

# El servicio se construye por solicitud con su propia sesión de base de datos.
ServiceDep = Annotated[EspacioService, Depends(get_espacio_service)]

EspacioId = Annotated[UUID, Path()]


@router.post(
    "",
    response_model=EspacioResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def crear_espacio(datos: EspacioCreateDTO, service: ServiceDep):
    try:
        espacio = service.crear(
            nombre=datos.nombre,
            tipo=datos.tipo,
            capacidad=datos.capacidad,
            estado=datos.estado,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return EspacioResponseDTO.model_validate(espacio)


@router.get("", response_model=EspacioPaginaDTO)
def listar_espacios(
    query: Annotated[EspacioQueryDTO, Query()],
    service: ServiceDep,
):
    espacios, total = service.listar(
        pagina=query.pagina,
        tamano=query.tamano,
        ordenar_por=query.ordenar_por,
        direccion=query.direccion,
        tipo=query.tipo.value if query.tipo else None,
        estado=query.estado.value if query.estado else None,
    )

    return EspacioPaginaDTO(
        items=[
            EspacioResponseDTO.model_validate(espacio)
            for espacio in espacios
        ],
        total=total,
        pagina=query.pagina,
        limite=query.tamano,
        total_paginas=(total + query.tamano - 1) // query.tamano,
    )


@router.get(
    "/{espacio_id}",
    response_model=EspacioResponseDTO,
)
def obtener_espacio(espacio_id: EspacioId, service: ServiceDep):
    espacio = service.obtener(espacio_id)

    if espacio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El espacio no existe.",
        )

    return EspacioResponseDTO.model_validate(espacio)


@router.put(
    "/{espacio_id}",
    response_model=EspacioResponseDTO,
)
def actualizar_espacio(
    espacio_id: EspacioId,
    datos: EspacioUpdateDTO,
    service: ServiceDep,
):
    try:
        espacio = service.actualizar(
            espacio_id=espacio_id,
            nombre=datos.nombre,
            tipo=datos.tipo,
            capacidad=datos.capacidad,
            estado=datos.estado,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if espacio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El espacio no existe.",
        )

    return EspacioResponseDTO.model_validate(espacio)


@router.delete(
    "/{espacio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_espacio(espacio_id: EspacioId, service: ServiceDep):
    try:
        eliminado = service.eliminar(espacio_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El espacio no existe.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
