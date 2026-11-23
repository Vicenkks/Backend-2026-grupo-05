import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from domain.auth import Unauthorized

PASSWORD_HASHER = PasswordHasher()


def now():
    return datetime.now(UTC)


def secret():
    value = os.getenv("JWT_SECRET", "")
    if len(value.encode()) < 32:
        raise RuntimeError("Configura JWT_SECRET con al menos 32 bytes aleatorios.")
    return value


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def attempt_key(purpose, identifier):
    return hmac.new(
        secret().encode(), f"{purpose}:{identifier}".encode(), hashlib.sha256
    ).hexdigest()


def hash_password(password):
    return PASSWORD_HASHER.hash(password)


def verify_password(encoded, password):
    try:
        return PASSWORD_HASHER.verify(encoded, password)
    except VerificationError, InvalidHashError:
        return False


@lru_cache(maxsize=1)
def dummy_hash():
    # Mismo trabajo de hashing para cuentas inexistentes.
    return hash_password("dummy-not-a-real-password")


def encode_token(user, purpose="access", jti=None):
    current = now()
    payload = {
        "sub": str(user.id),
        "exp": current + timedelta(minutes=15),
        "iat": current,
        "type": purpose,
        "ver": user.token_version,
        "iss": "coworking-api",
        "aud": "coworking",
    }
    if jti is not None:
        payload["jti"] = str(jti)
    return jwt.encode(payload, secret(), algorithm="HS256")


def decode_token(token, purpose):
    try:
        claims = jwt.decode(
            token,
            secret(),
            algorithms=["HS256"],
            issuer="coworking-api",
            audience="coworking",
            options={"require": ["sub", "exp", "iat", "type", "ver"]},
        )
        UUID(claims["sub"])
        if claims["type"] != purpose or type(claims["ver"]) is not int:
            raise ValueError()
        if purpose == "recovery":
            UUID(claims["jti"])
        return claims
    except jwt.InvalidTokenError, ValueError, KeyError, TypeError, AttributeError:
        raise Unauthorized("Token inválido o vencido.") from None
