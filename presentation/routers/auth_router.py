from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from presentation.schemas.dtos.auth_dto import (
    LoginDTO,
    MessageDTO,
    RecoveryDTO,
    RecoveryResponseDTO,
    RegisterDTO,
    ResetDTO,
    TokenDTO,
    UserDTO,
)
from presentation.security.auth import (
    AuthDep,
    UserDep,
    check_origin,
    clear_session_cookies,
    refresh_cookie,
    set_session_cookies,
)

router = APIRouter(
    prefix="/auth", tags=["Autenticación"], dependencies=[Depends(check_origin)]
)


@router.post(
    "/registro", summary="Crear cuenta", response_model=UserDTO, status_code=201
)
def register(data: RegisterDTO, service: AuthDep):
    """Registra una cuenta con rol de lector."""
    return service.register(str(data.email), data.password.get_secret_value())


@router.post("/login", summary="Iniciar sesión", response_model=TokenDTO)
def login(data: LoginDTO, service: AuthDep, response: Response):
    """Inicia sesión con tu correo y contraseña. Se permiten 5 intentos cada 15 minutos."""
    access, refresh = service.login(str(data.email), data.password.get_secret_value())
    set_session_cookies(response, refresh)
    return TokenDTO(access_token=access)


@router.get("/me", summary="Ver mi cuenta", response_model=UserDTO)
def me(user: UserDep, response: Response):
    """Muestra los datos de la cuenta con la que iniciaste sesión."""
    response.headers["Cache-Control"] = "no-store"
    return user


@router.post("/refresh", summary="Renovar sesión", response_model=TokenDTO)
def refresh(service: AuthDep, response: Response, raw: str = Depends(refresh_cookie)):
    """Renueva el acceso usando la cookie que recibiste al iniciar sesión."""
    access, replacement = service.refresh(raw)
    set_session_cookies(response, replacement)
    return TokenDTO(access_token=access)


@router.post("/logout", summary="Cerrar sesión", status_code=204)
def logout(service: AuthDep, response: Response, raw: str = Depends(refresh_cookie)):
    """Cierra la sesión e impide renovarla. El token de acceso vence en un máximo de 15 minutos."""
    service.logout(raw)
    clear_session_cookies(response)


@router.post(
    "/recuperacion",
    summary="Solicitar cambio de contraseña",
    response_model=RecoveryResponseDTO,
    status_code=202,
)
def recovery(data: RecoveryDTO, service: AuthDep, request: Request, response: Response):
    """Devuelve un enlace para cambiar la contraseña. El enlace aparece en la respuesta; no se envía por correo."""
    token = service.request_recovery(str(data.email))
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return RecoveryResponseDTO(
        message="Si el correo está registrado y no superaste el límite de solicitudes, usa este enlace para cambiar tu contraseña. Vence en 15 minutos y solo sirve una vez.",
        reset_link=str(request.url_for("reset")) + "?" + urlencode({"token": token}),
    )


@router.post("/restablecer", summary="Cambiar contraseña", response_model=MessageDTO)
def reset(
    data: ResetDTO,
    service: AuthDep,
    response: Response,
    token: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=4096,
            description="Token del enlace de recuperación. También puedes enviarlo en el cuerpo JSON.",
        ),
    ] = None,
):
    """Envía un POST al enlace recibido con la nueva contraseña en el campo password. Después tendrás que iniciar sesión de nuevo."""
    body_token = data.token.get_secret_value() if data.token else None
    if token and body_token and token != body_token:
        raise HTTPException(
            422,
            "El token de la URL y el del cuerpo no coinciden. Envía solo el del enlace recibido.",
        )
    selected = token or body_token
    if not selected:
        raise HTTPException(422, "Falta el token del enlace de recuperación.")
    service.reset_password(selected, data.password.get_secret_value())
    clear_session_cookies(response)
    response.headers["Referrer-Policy"] = "no-referrer"
    return MessageDTO(
        message="Contraseña cambiada. Ya puedes iniciar sesión con la nueva clave."
    )
