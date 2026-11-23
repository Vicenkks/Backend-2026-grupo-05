from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import jwt
import pytest
from pydantic import ValidationError

from application.services.auth_service import AuthService
from domain.auth import Forbidden, Unauthorized, User, validate_password
from domain.errors import Conflict
from infrastructure.security import tokens
from presentation.schemas.dtos.auth_dto import RegisterDTO, ResetDTO

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("password", ["", "corta", "x" * 11, "x" * 129])
def test_password_policy(password):
    with pytest.raises(ValueError):
        validate_password(password)


@pytest.mark.parametrize("length", [12, 128])
def test_password_boundaries(length):
    validate_password("a" * length)


def test_hash_is_argon2_and_verifies():
    encoded = tokens.hash_password("password-seguro")
    assert encoded.startswith("$argon2id$")
    assert tokens.verify_password(encoded, "password-seguro")
    assert not tokens.verify_password(encoded, "otra-password")
    assert not tokens.verify_password("invalid-hash", "password-seguro")


def test_role_permissions():
    user = User(uuid4(), "a@example.com", "hidden")
    with pytest.raises(Forbidden):
        user.require_admin()
    user.role = "admin"
    user.require_admin()
    assert "hidden" not in repr(user)


@pytest.mark.parametrize(
    "extra", [{"role": "admin"}, {"active": True}, {"token_version": 0}]
)
def test_registration_cannot_escalate_privileges(extra):
    with pytest.raises(ValidationError):
        RegisterDTO(email="a@example.com", password="password-seguro", **extra)


def test_reset_cannot_select_another_user():
    with pytest.raises(ValidationError):
        ResetDTO(token="token", password="password-seguro", user_id=str(uuid4()))


def test_access_claims():
    user = User(uuid4(), "a@example.com", "secret")
    token = tokens.encode_token(user)
    claims = tokens.decode_token(token, "access")
    assert claims["sub"] == str(user.id)
    assert claims["ver"] == 0
    assert claims["exp"] - claims["iat"] == 900
    assert "password_hash" not in claims and "email" not in claims


@pytest.mark.parametrize(
    "change",
    [
        {"exp": 1},
        {"type": "recovery"},
        {"sub": "bad"},
        {"ver": "0"},
        {"aud": "elsewhere"},
        {"iss": "elsewhere"},
    ],
)
def test_invalid_claims(change):
    token = tokens.encode_token(User(uuid4(), "a@example.com", "secret"))
    claims = jwt.decode(token, options={"verify_signature": False})
    claims.update(change)
    with pytest.raises(Unauthorized):
        tokens.decode_token(
            jwt.encode(claims, tokens.secret(), algorithm="HS256"), "access"
        )


@pytest.mark.parametrize("kind", ["signature", "algorithm", "missing_exp", "garbage"])
def test_untrusted_tokens(kind):
    token = tokens.encode_token(User(uuid4(), "a@example.com", "secret"))
    claims = jwt.decode(token, options={"verify_signature": False})
    if kind == "signature":
        token = jwt.encode(claims, "other-secret" * 8, algorithm="HS256")
    elif kind == "algorithm":
        token = jwt.encode(claims, tokens.secret(), algorithm="HS384")
    elif kind == "missing_exp":
        del claims["exp"]
        token = jwt.encode(claims, tokens.secret(), algorithm="HS256")
    else:
        token = "not.a.jwt"
    with pytest.raises(Unauthorized):
        tokens.decode_token(token, "access")


def test_secret_required(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "")
    with pytest.raises(RuntimeError):
        tokens.secret()


def test_duplicate_account_stops_write():
    repository = MagicMock()
    repository.user.return_value = object()
    with pytest.raises(Conflict):
        AuthService(repository).register("A@example.com", "password-seguro")
    repository.user.assert_called_once_with(email="a@example.com")
    repository.add.assert_not_called()


def test_failed_login_records_attempt_without_session():
    repository = MagicMock()
    repository.user.return_value = None
    with pytest.raises(Unauthorized):
        AuthService(repository).login("nobody@example.com", "incorrect-password")
    repository.commit_security_event.assert_called_once()
    repository.add.assert_not_called()


def test_replayed_refresh_revokes_family():
    repository = MagicMock()
    record = SimpleNamespace(
        user_id=uuid4(), family_id=uuid4(), used=True, revoked=False
    )
    repository.refresh.return_value = record
    with pytest.raises(Unauthorized):
        AuthService(repository).refresh("old-token")
    repository.revoke.assert_called_once_with(record.user_id, record.family_id)
    repository.commit_security_event.assert_called_once()
    repository.add.assert_not_called()


def test_secure_cookies_by_default(monkeypatch):
    from starlette.responses import Response

    from presentation.security.auth import set_session_cookies

    monkeypatch.delenv("COOKIE_SECURE", raising=False)
    response = Response()
    set_session_cookies(response, "opaque-refresh")
    headers = [
        h for h in response.headers.getlist("set-cookie") if "Max-Age=0" not in h
    ]
    assert all("Secure" in header and "SameSite=strict" in header for header in headers)
    assert "HttpOnly" in headers[0]


def test_cors_rejects_wildcard(monkeypatch):
    from presentation.security.auth import allowed_origins

    monkeypatch.setenv("ALLOWED_ORIGINS", "*")
    with pytest.raises(RuntimeError):
        allowed_origins()


def test_reset_token_is_not_logged():
    import logging

    from presentation.docs import RedactQuery

    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        "",
        1,
        "%s %s %s %s %s",
        ("client", "POST", "/auth/restablecer?token=private-value", "1.1", 200),
        None,
    )
    assert RedactQuery().filter(record)
    assert "private-value" not in record.getMessage()
    assert "/auth/restablecer" in record.getMessage()
    record.args = None
    assert RedactQuery().filter(record)
