
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

from application.services.empresa_service import EmpresaService
from presentation.dependencies import get_empresa_service
from presentation.schemas.dtos.empresa_dto import (
    EmpresaCreateDTO,
    EmpresaUpdateDTO,
    EmpresaResponseDTO,
    EmpresaPaginaDTO,
)
from presentation.schemas.dtos.empresa_query_dto import EmpresaQueryDTO


router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"],
)

ServiceDep = Annotated[EmpresaService, Depends(get_empresa_service)]
EmpresaId = Annotated[UUID, Path()]


@router.post(
    "",
    response_model=EmpresaResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def crear_empresa(datos: EmpresaCreateDTO, service: ServiceDep):
    try:
        empresa = service.crear(
            nombre=datos.nombre,
            rut=datos.rut,
            contacto=datos.contacto,
            activa=datos.activa,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return EmpresaResponseDTO.model_validate(empresa)


@router.get("", response_model=EmpresaPaginaDTO)
def listar_empresas(
    query: Annotated[EmpresaQueryDTO, Query()],
    service: ServiceDep,
):
    empresas, total = service.listar(
        pagina=query.pagina,
        tamano=query.tamano,
        activa=query.activa,
    )

    return EmpresaPaginaDTO(
        items=[
            EmpresaResponseDTO.model_validate(empresa)
            for empresa in empresas
        ],
        total=total,
        pagina=query.pagina,
        limite=query.tamano,
        total_paginas=(total + query.tamano - 1) // query.tamano,
    )


@router.get(
    "/{empresa_id}",
    response_model=EmpresaResponseDTO,
)
def obtener_empresa(empresa_id: EmpresaId, service: ServiceDep):
    empresa = service.obtener(empresa_id)

    if empresa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa no existe.",
        )

    return EmpresaResponseDTO.model_validate(empresa)


@router.put(
    "/{empresa_id}",
    response_model=EmpresaResponseDTO,
)
def actualizar_empresa(
    empresa_id: EmpresaId,
    datos: EmpresaUpdateDTO,
    service: ServiceDep,
):
    try:
        empresa = service.actualizar(
            empresa_id=empresa_id,
            nombre=datos.nombre,
            rut=datos.rut,
            contacto=datos.contacto,
            activa=datos.activa,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if empresa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa no existe.",
        )

    return EmpresaResponseDTO.model_validate(empresa)


@router.delete(
    "/{empresa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_empresa(empresa_id: EmpresaId, service: ServiceDep):
    try:
        eliminada = service.eliminar(empresa_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa no existe.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
