"""Administración local: uv run python -m scripts.set_role EMAIL admin|lector."""

import argparse

from domain.errors import ResourceNotFound
from infrastructure.database import SessionLocal
from infrastructure.repositories.auth_repository import AuthRepository


def set_role(email, role):
    with SessionLocal.begin() as session:
        user = AuthRepository(session).user(email=email.strip().lower(), lock=True)
        if user is None:
            raise ResourceNotFound(
                "Registra primero la cuenta mediante /auth/registro."
            )
        user.role = role
        user.token_version += 1
        AuthRepository(session).revoke(user.id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email")
    parser.add_argument("role", choices=["admin", "lector"])
    args = parser.parse_args()
    set_role(args.email, args.role)
    print("Rol actualizado; sesiones anteriores revocadas.")
