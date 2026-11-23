from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from domain.auth import User
from infrastructure.models.auth_model import (
    AttemptModel,
    RecoveryModel,
    RefreshModel,
    UserModel,
)


class AuthRepository:
    def __init__(self, session):
        self.session = session

    def user(self, *, email=None, user_id=None, lock=False):
        query = select(UserModel).where(
            UserModel.email == email if email is not None else UserModel.id == user_id
        )
        if lock:
            query = query.with_for_update().execution_options(populate_existing=True)
        return self.session.scalar(query)

    @staticmethod
    def identity(model):
        return User(
            model.id,
            model.email,
            model.password_hash,
            model.role,
            model.active,
            model.token_version,
        )

    def add(self, model):
        self.session.add(model)
        self.session.flush()
        return model

    def refresh(self, token_hash):
        return self.session.scalar(
            select(RefreshModel)
            .where(RefreshModel.token_hash == token_hash)
            .execution_options(populate_existing=True)
        )

    def recovery(self, jti):
        return self.session.get(RecoveryModel, jti)

    def revoke(self, user_id, family_id=None):
        query = update(RefreshModel).where(RefreshModel.user_id == user_id)
        if family_id is not None:
            query = query.where(RefreshModel.family_id == family_id)
        self.session.execute(query.values(revoked=True))

    def invalidate_recoveries(self, user_id):
        self.session.execute(
            update(RecoveryModel)
            .where(RecoveryModel.user_id == user_id)
            .values(used=True)
        )

    def attempt(self, key, current, limit):
        self.session.execute(
            insert(AttemptModel)
            .values(key=key, started_at=current, count=0)
            .on_conflict_do_nothing(index_elements=["key"])
        )
        record = self.session.scalar(
            select(AttemptModel).where(AttemptModel.key == key).with_for_update()
        )
        if current >= record.started_at + timedelta(minutes=15):
            record.started_at, record.count = current, 0
        if record.count >= limit:
            return False
        record.count += 1
        self.session.flush()
        return True

    def commit_security_event(self):
        # Los intentos fallidos y la revocación por replay sobreviven al error HTTP.
        self.session.commit()
