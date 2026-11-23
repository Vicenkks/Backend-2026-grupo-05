from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from domain.auth import Unauthorized
from infrastructure.models.auth_model import (
    AttemptModel,
    RecoveryModel,
    RefreshModel,
    UserModel,
)
from infrastructure.security import tokens

pytestmark = pytest.mark.integration
PASSWORD = "Una-clave-de-prueba-2026"


def test_user_persistence_and_normalization(service, db, database):
    user = service.register("PERSONA@example.com", PASSWORD)
    db.commit()
    with database[1]() as other:
        saved = other.get(UserModel, user.id)
        assert saved.email == "persona@example.com"
        assert saved.role == "lector"
        assert saved.password_hash != PASSWORD
        assert tokens.verify_password(saved.password_hash, PASSWORD)


def test_database_unique_email(service, db):
    service.register("persona@example.com", PASSWORD)
    db.commit()
    db.add(UserModel(email="persona@example.com", password_hash="irrelevant"))
    with pytest.raises(IntegrityError):
        db.flush()
    db.rollback()


def test_refresh_foreign_key(db):
    db.add(
        RefreshModel(
            user_id=uuid4(),
            family_id=uuid4(),
            token_hash="a" * 64,
            expires_at=tokens.now(),
        )
    )
    with pytest.raises(IntegrityError):
        db.flush()
    db.rollback()


def test_rotation_and_replay_persist_revocation(service, db, database):
    service.register("persona@example.com", PASSWORD)
    _, old = service.login("persona@example.com", PASSWORD)
    db.commit()
    _, new = service.refresh(old)
    db.commit()
    records = db.scalars(select(RefreshModel)).all()
    assert len(records) == 2
    assert {r.token_hash for r in records} == {tokens.digest(old), tokens.digest(new)}
    assert any(r.used for r in records)
    with pytest.raises(Unauthorized):
        service.refresh(old)
    db.rollback()
    with database[1]() as other:
        assert all(r.revoked for r in other.scalars(select(RefreshModel)))
    with pytest.raises(Unauthorized):
        service.refresh(new)


def test_logout_only_revokes_current_family(service, db):
    service.register("persona@example.com", PASSWORD)
    access, first = service.login("persona@example.com", PASSWORD)
    _, second = service.login("persona@example.com", PASSWORD)
    service.logout(first)
    db.commit()
    with pytest.raises(Unauthorized):
        service.refresh(first)
    assert service.refresh(second)[0]
    assert service.current_user(access).email == "persona@example.com"


def test_login_limit_survives_rollback(service, db):
    service.register("persona@example.com", PASSWORD)
    db.commit()
    for _ in range(5):
        with pytest.raises(Unauthorized):
            service.login("persona@example.com", "wrong-password")
        db.rollback()
    with pytest.raises(Unauthorized):
        service.login("persona@example.com", PASSWORD)
    attempt = db.scalar(select(AttemptModel))
    assert attempt.count == 5
    attempt.started_at -= timedelta(minutes=16)
    db.commit()
    assert service.login("persona@example.com", PASSWORD)[0]


def test_reset_consumes_and_invalidates_all_sessions(service, db):
    user = service.register("persona@example.com", PASSWORD)
    access, refresh = service.login("persona@example.com", PASSWORD)
    jti, other_jti = uuid4(), uuid4()
    for identifier in [jti, other_jti]:
        db.add(
            RecoveryModel(
                id=identifier,
                user_id=user.id,
                expires_at=tokens.now() + timedelta(minutes=15),
            )
        )
    db.commit()
    token = tokens.encode_token(user, "recovery", jti)
    service.reset_password(token, "Una-nueva-clave-2026")
    db.commit()
    assert all(r.used for r in db.scalars(select(RecoveryModel)))
    for action in [
        lambda: service.current_user(access),
        lambda: service.refresh(refresh),
        lambda: service.reset_password(token, "Otra-nueva-clave-2026"),
    ]:
        with pytest.raises(Unauthorized):
            action()
    with pytest.raises(Unauthorized):
        service.login(user.email, PASSWORD)
    assert service.login(user.email, "Una-nueva-clave-2026")[0]


@pytest.mark.parametrize("condition", ["expired", "inactive", "unknown"])
def test_invalid_refresh(service, db, condition):
    user = service.register("persona@example.com", PASSWORD)
    _, raw = service.login(user.email, PASSWORD)
    if condition == "expired":
        db.scalar(select(RefreshModel)).expires_at = tokens.now() - timedelta(seconds=1)
    elif condition == "inactive":
        db.get(UserModel, user.id).active = False
    else:
        raw = "nonexistent"
    db.commit()
    with pytest.raises(Unauthorized):
        service.refresh(raw)


def test_recovery_rate_does_not_lock_login(service, db):
    service.register("persona@example.com", PASSWORD)
    for _ in range(4):
        token = service.request_recovery("persona@example.com")
        db.commit()
    assert len(db.scalars(select(RecoveryModel)).all()) == 3
    with pytest.raises(Unauthorized):
        service.reset_password(token, "Nueva-password-segura")
    assert service.login("persona@example.com", PASSWORD)[0]


def test_concurrent_refresh_only_one_rotation(service, db, database):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from application.services.auth_service import AuthService
    from infrastructure.repositories.auth_repository import AuthRepository

    service.register("persona@example.com", PASSWORD)
    _, raw = service.login("persona@example.com", PASSWORD)
    db.commit()
    barrier = Barrier(2)

    def rotate():
        with database[1]() as session:
            concurrent = AuthService(AuthRepository(session))
            barrier.wait(timeout=5)
            try:
                result = concurrent.refresh(raw)
                session.commit()
                return result
            except Unauthorized:
                session.rollback()
                return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: rotate(), range(2)))
    assert sum(result is not None for result in results) == 1
    with database[1]() as session:
        records = session.scalars(select(RefreshModel)).all()
        assert len(records) == 2
        assert all(record.revoked for record in records)


def test_concurrent_recovery_consumed_once(service, db, database):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from application.services.auth_service import AuthService
    from infrastructure.repositories.auth_repository import AuthRepository

    user = service.register("persona@example.com", PASSWORD)
    jti = uuid4()
    db.add(
        RecoveryModel(
            id=jti, user_id=user.id, expires_at=tokens.now() + timedelta(minutes=15)
        )
    )
    db.commit()
    token = tokens.encode_token(user, "recovery", jti)
    barrier = Barrier(2)

    def consume():
        with database[1]() as session:
            concurrent = AuthService(AuthRepository(session))
            barrier.wait(timeout=5)
            try:
                concurrent.reset_password(token, "Otra-password-segura")
                session.commit()
                return True
            except Unauthorized:
                session.rollback()
                return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(lambda _: consume(), range(2))) == [False, True]


@pytest.mark.parametrize("kind", ["expired", "used", "missing", "other_account"])
def test_recovery_requires_valid_persisted_permission(service, db, kind):
    user = service.register("persona@example.com", PASSWORD)
    other = service.register("otra@example.com", PASSWORD)
    jti = uuid4()
    if kind != "missing":
        db.add(
            RecoveryModel(
                id=jti,
                user_id=other.id if kind == "other_account" else user.id,
                expires_at=tokens.now()
                + timedelta(minutes=-1 if kind == "expired" else 15),
                used=kind == "used",
            )
        )
    db.commit()
    before = db.get(UserModel, user.id).password_hash
    with pytest.raises(Unauthorized):
        service.reset_password(
            tokens.encode_token(user, "recovery", jti), "Una-clave-distinta-2026"
        )
    assert db.get(UserModel, user.id).password_hash == before
