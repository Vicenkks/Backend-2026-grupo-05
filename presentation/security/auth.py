import os
from typing import Annotated

from fastapi import Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application.services.auth_service import AuthService
from domain.auth import Forbidden, Unauthorized, User
from infrastructure.repositories.auth_repository import AuthRepository
from presentation.dependencies import SessionDep

bearer = HTTPBearer(auto_error=False)


def get_auth_service(session: SessionDep):
    return AuthService(AuthRepository(session))


AuthDep = Annotated[AuthService, Depends(get_auth_service)]


def current_user(
    service: AuthDep,
    credential: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if credential is None:
        raise Unauthorized("Inicia sesión y envía tu token de acceso.")
    return service.current_user(credential.credentials)


UserDep = Annotated[User, Depends(current_user)]


def business_permission(request: Request, user: UserDep):
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        user.require_admin()


def allowed_origins():
    origins = [
        item.strip()
        for item in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
        if item.strip()
    ]
    if "*" in origins:
        raise RuntimeError(
            "ALLOWED_ORIGINS requiere orígenes explícitos con credenciales."
        )
    return origins


def check_origin(request: Request):
    origin = request.headers.get("origin")
    if origin and origin not in allowed_origins():
        raise Forbidden("Origen no permitido.")


def refresh_cookie(request: Request):
    check_origin(request)
    raw = request.cookies.get("refresh_token")
    if not raw:
        raise Unauthorized("Sesión inválida.")
    return raw


def set_session_cookies(response: Response, raw):
    secure = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    response.set_cookie(
        "refresh_token",
        raw,
        max_age=7 * 86400,
        httponly=True,
        secure=secure,
        samesite="strict",
        path="/auth",
    )
    response.headers["Cache-Control"] = "no-store"


def clear_session_cookies(response: Response):
    response.delete_cookie("refresh_token", path="/auth")
    response.headers["Cache-Control"] = "no-store"
