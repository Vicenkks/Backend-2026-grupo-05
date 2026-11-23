from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import jwt
import pytest

from infrastructure.models.auth_model import UserModel
from infrastructure.security import tokens

pytestmark = pytest.mark.e2e
PASSWORD = "Una-clave-de-prueba-2026"
SPACE = {
    "nombre": "Sala de pruebas",
    "tipo": "oficina",
    "capacidad": 4,
    "estado": "activo",
}


def recovery_token(client):
    response = client.post("/auth/recuperacion", json={"email": "persona@example.com"})
    assert response.status_code == 202
    return parse_qs(urlsplit(response.json()["reset_link"]).query)["token"][0]


def test_access_business_logout(client, account, login, db):
    account_data = account()
    db.get(UserModel, UUID(account_data["id"])).role = "admin"
    db.commit()
    login()
    response = client.post("/espacios", json=SPACE)
    assert response.status_code == 201
    space_id = response.json()["id"]
    assert client.get(f"/espacios/{space_id}").json()["nombre"] == SPACE["nombre"]
    raw = client.cookies["refresh_token"]
    assert client.post("/auth/logout").status_code == 204
    assert "refresh_token" not in client.cookies
    response = client.post(
        "/auth/refresh",
        headers={
            "Cookie": f"refresh_token={raw}",
        },
    )
    assert response.status_code == 401


def test_recovery_complete_flow(client, account, login):
    account()
    old_access = login()
    old_raw = client.cookies["refresh_token"]
    response = client.post("/auth/recuperacion", json={"email": "persona@example.com"})
    assert response.status_code == 202
    link = response.json()["reset_link"]
    body = {"password": "Una-clave-nueva-2026"}
    assert client.post(link, json=body).status_code == 200
    assert client.post(link, json=body).status_code == 401
    assert (
        client.get(
            "/auth/me", headers={"Authorization": "Bearer " + old_access}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/refresh",
            headers={
                "Cookie": f"refresh_token={old_raw}",
            },
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/login", json={"email": "persona@example.com", "password": PASSWORD}
        ).status_code
        == 401
    )
    login(password=body["password"])
    assert client.get("/auth/me").status_code == 200


def test_differentiated_permissions(client, account, login, db):
    assert client.post("/espacios", json=SPACE).status_code == 401
    user = account()
    login()
    assert client.post("/espacios", json=SPACE).status_code == 403
    assert client.get("/espacios").status_code == 200
    db.get(UserModel, UUID(user["id"])).role = "admin"
    db.commit()
    response = client.post("/espacios", json=SPACE)
    assert response.status_code == 201
    assert client.get("/espacios/" + response.json()["id"]).json()["capacidad"] == 4


def test_refresh_rotation_replay_revokes_replacement(client, account, login):
    account()
    login()
    raw = client.cookies["refresh_token"]
    assert client.post("/auth/refresh").status_code == 200
    replacement = client.cookies["refresh_token"]
    assert replacement != raw
    assert (
        client.post(
            "/auth/refresh",
            headers={
                "Cookie": f"refresh_token={raw}",
            },
        ).status_code
        == 401
    )
    assert client.post("/auth/refresh").status_code == 401


@pytest.mark.parametrize(
    "path", ["/espacios", "/empresas", "/disponibilidades", "/reservas"]
)
@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_business_routes_protected(client, path, method):
    if method in ("PUT", "DELETE"):
        if path == "/reservas":
            path += "/00000000-0000-0000-0000-000000000001/cancelar"
            method = "POST"
        else:
            path += "/00000000-0000-0000-0000-000000000001"
    assert client.request(method, path, json={}).status_code == 401


@pytest.mark.parametrize(
    "changes", [{"role": "admin"}, {"password": "short"}, {"email": "invalid"}]
)
def test_registration_validation(client, changes):
    body = {"email": "persona@example.com", "password": PASSWORD, **changes}
    response = client.post("/auth/registro", json=body)
    assert response.status_code == 422
    assert body["password"] not in response.text


def test_duplicate_and_safe_dto(client, account, login):
    user = account()
    assert set(user) == {"id", "email", "role", "active"}
    assert user["role"] == "lector"
    response = client.post(
        "/auth/registro", json={"email": "PERSONA@example.com", "password": PASSWORD}
    )
    assert response.status_code == 409
    login()
    assert set(client.get("/auth/me").json()) == set(user)


@pytest.mark.parametrize("kind", ["expired", "purpose", "tampered"])
def test_reject_bad_access(client, account, login, kind):
    account()
    token = login()
    claims = jwt.decode(token, options={"verify_signature": False})
    if kind == "expired":
        claims["exp"] = 1
    if kind == "purpose":
        claims["type"] = "recovery"
    bad = jwt.encode(
        claims,
        tokens.secret() if kind != "tampered" else "bad-secret" * 8,
        algorithm="HS256",
    )
    response = client.get("/auth/me", headers={"Authorization": "Bearer " + bad})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "kind", ["expired", "purpose", "tampered", "different_user", "same_password"]
)
def test_reject_bad_reset_without_changing_password(client, account, login, kind):
    account()
    access = login()
    token = recovery_token(client)
    claims = jwt.decode(token, options={"verify_signature": False})
    body = {"token": token, "password": "Nueva-password-2026"}
    if kind == "expired":
        claims["exp"] = 1
        body["token"] = jwt.encode(claims, tokens.secret(), algorithm="HS256")
    elif kind == "purpose":
        body["token"] = access
    elif kind == "tampered":
        body["token"] = jwt.encode(claims, "bad-secret" * 8, algorithm="HS256")
    elif kind == "different_user":
        other = account(email="otra@example.com")
        body["user_id"] = other["id"]
    else:
        body["password"] = PASSWORD
    response = client.post("/auth/restablecer", json=body)
    assert response.status_code == (
        422 if kind == "different_user" else 400 if kind == "same_password" else 401
    )
    assert login()


def test_recovery_generic_and_limited(client, account, login):
    account()
    known = client.post("/auth/recuperacion", json={"email": "persona@example.com"})
    unknown = client.post("/auth/recuperacion", json={"email": "missing@example.com"})
    assert known.status_code == unknown.status_code == 202
    assert known.json()["message"] == unknown.json()["message"]
    assert set(known.json()) == set(unknown.json()) == {"message", "reset_link"}
    assert (
        client.post(
            unknown.json()["reset_link"], json={"password": "Nueva-clave-segura"}
        ).status_code
        == 401
    )
    for _ in range(3):
        limited = client.post(
            "/auth/recuperacion", json={"email": "persona@example.com"}
        )
    assert (
        client.post(
            limited.json()["reset_link"], json={"password": "Nueva-clave-segura"}
        ).status_code
        == 401
    )
    assert login()


def test_login_lockout(client, account):
    account()
    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={"email": "persona@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert "access_token" not in response.json()
        assert "refresh_token" not in client.cookies
    assert (
        client.post(
            "/auth/login", json={"email": "persona@example.com", "password": PASSWORD}
        ).status_code
        == 401
    )


def test_origin_and_cookie_flags(client, account, login):
    account()
    login()
    assert "csrf_token" not in client.cookies
    assert client.post("/auth/refresh").status_code == 200
    assert (
        client.post(
            "/auth/refresh", headers={"Origin": "https://attacker.example"}
        ).status_code
        == 403
    )
    response = client.post(
        "/auth/login", json={"email": "persona@example.com", "password": PASSWORD}
    )
    refresh = next(
        value
        for value in response.headers.get_list("set-cookie")
        if value.startswith("refresh_token=")
    )
    assert (
        "HttpOnly" in refresh
        and "SameSite=strict" in refresh
        and "Path=/auth" in refresh
    )
    assert response.headers["cache-control"] == "no-store"


def test_inactive_user_loses_access(client, account, login, db):
    user = account()
    login()
    db.get(UserModel, UUID(user["id"])).active = False
    db.commit()
    assert client.get("/auth/me").status_code == 401
    assert (
        client.post(
            "/auth/login", json={"email": "persona@example.com", "password": PASSWORD}
        ).status_code
        == 401
    )


def test_openapi_security(client):
    schema = client.get("/openapi.json").json()
    assert schema["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
    assert schema["paths"]["/espacios"]["post"]["security"]
    assert not schema["paths"]["/auth/login"]["post"].get("security")
    assert {"401", "403"} <= schema["paths"]["/reservas"]["post"]["responses"].keys()


def test_unknown_login_is_generic(client, account):
    account()
    known = client.post(
        "/auth/login",
        json={"email": "persona@example.com", "password": "wrong-password"},
    )
    unknown = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "wrong-password"},
    )
    assert known.status_code == unknown.status_code == 401
    assert known.json() == unknown.json()


def test_cors_explicit_origin(client, api):
    response = client.options(
        "/auth/refresh",
        headers={
            "Origin": api,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == api
    assert response.headers["access-control-allow-credentials"] == "true"
    response = client.options(
        "/auth/refresh",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize("path", ["/auth/refresh", "/auth/logout"])
def test_without_refresh_is_unauthorized(client, path):
    assert client.post(path).status_code == 401


def test_swagger_has_no_csrf_parameter(client):
    schema = client.get("/openapi.json").json()
    for path in ["/auth/logout", "/auth/refresh"]:
        assert not schema["paths"][path]["post"].get("parameters")


@pytest.mark.parametrize("path", ["/auth/registro", "/auth/login"])
def test_register_login_need_no_authorization(client, path):
    credentials = {"email": "public@example.com", "password": PASSWORD}
    if path == "/auth/login":
        assert client.post("/auth/registro", json=credentials).status_code == 201
    response = client.post(path, json=credentials)
    assert response.status_code == (201 if path.endswith("registro") else 200)
    schema = client.get("/openapi.json").json()
    assert not schema["paths"][path]["post"].get("security")


def test_reset_requires_one_token(client):
    assert (
        client.post("/auth/restablecer", json={"password": PASSWORD}).status_code == 422
    )
    assert (
        client.post(
            "/auth/restablecer?token=one", json={"password": PASSWORD, "token": "two"}
        ).status_code
        == 422
    )


def test_swagger_session_assets(client):
    page = client.get("/docs")
    assert page.status_code == 200
    assert "/docs/session.js" in page.text
    script = client.get("/docs/session.js")
    assert script.status_code == 200
    assert script.headers["cache-control"] == "no-store"
