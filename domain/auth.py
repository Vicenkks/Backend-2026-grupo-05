"""Identidad de acceso y reglas independientes del transporte HTTP."""

from dataclasses import dataclass, field
from uuid import UUID

from domain.errors import DomainError


class Unauthorized(DomainError):
    pass


class Forbidden(DomainError):
    pass


def validate_password(password: str) -> None:
    if not 12 <= len(password) <= 128:
        raise ValueError("La contraseña debe tener entre 12 y 128 caracteres.")


@dataclass
class User:
    id: UUID
    email: str
    password_hash: str = field(repr=False)
    role: str = "lector"
    active: bool = True
    token_version: int = 0

    def require_admin(self) -> None:
        if self.role != "admin":
            raise Forbidden("Necesitas una cuenta de administrador para hacer esto.")
