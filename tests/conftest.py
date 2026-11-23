"""Cada ejecución usa bases PostgreSQL descartables."""

import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import psycopg2
import pytest
from psycopg2 import sql

ROOT = Path(__file__).resolve().parents[1]
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg2://coworking_test:test_only_password@127.0.0.1:55432/unused_test"
)
os.environ["JWT_SECRET"] = secrets.token_urlsafe(48)
os.environ["COOKIE_SECURE"] = "false"
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "55432"
os.environ["DB_USER"] = "coworking_test"
os.environ["DB_PASSWORD"] = "test_only_password"
PASSWORD = "Una-clave-de-prueba-2026"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def database():
    from uuid import uuid4

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    name = "coworking_" + uuid4().hex + "_test"
    connection = psycopg2.connect(
        host="127.0.0.1",
        port=55432,
        user="coworking_test",
        password="test_only_password",
        dbname="postgres",
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    url = f"postgresql+psycopg2://coworking_test:test_only_password@127.0.0.1:55432/{name}"
    env = dict(os.environ, DATABASE_URL=url)
    engine = create_engine(url)
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [sys.executable, "-m", "alembic", "check"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
        )
        yield url, sessionmaker(engine, expire_on_commit=False)
    finally:
        engine.dispose()
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name))
            )
        connection.close()


@pytest.fixture
def db(database):
    from sqlalchemy import text

    _, factory = database
    with factory.begin() as session:
        session.execute(
            text(
                "TRUNCATE auth_attempts, recovery_tokens, refresh_tokens, users, reservas, disponibilidades, empresas, espacios CASCADE"
            )
        )
    with factory() as session:
        yield session
        session.rollback()


@pytest.fixture
def service(db):
    from application.services.auth_service import AuthService
    from infrastructure.repositories.auth_repository import AuthRepository

    return AuthService(AuthRepository(db))


@pytest.fixture(scope="session")
def api(database, tmp_path_factory):
    url, _ = database
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    env = dict(
        os.environ,
        DATABASE_URL=url,
        ALLOWED_ORIGINS=base,
    )
    with (tmp_path_factory.mktemp("server") / "server.log").open("w+") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=log,
        )
        try:
            for _ in range(100):
                try:
                    if httpx.get(base + "/health", timeout=0.5).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                if process.poll() is not None:
                    log.seek(0)
                    pytest.fail(log.read())
                time.sleep(0.1)
            else:
                pytest.fail("La API no inició")
            yield base
        finally:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


@pytest.fixture
def client(api, db):
    with httpx.Client(base_url=api, timeout=10) as client:
        yield client


@pytest.fixture
def account(client):
    def create(email="persona@example.com", password=PASSWORD):
        response = client.post(
            "/auth/registro", json={"email": email, "password": password}
        )
        assert response.status_code == 201, response.text
        return response.json()

    return create


@pytest.fixture
def login(client):
    def authenticate(email="persona@example.com", password=PASSWORD):
        response = client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == 200, response.text
        client.headers["Authorization"] = "Bearer " + response.json()["access_token"]
        return response.json()["access_token"]

    return authenticate
