import secrets
from datetime import timedelta
from uuid import UUID, uuid4

from domain.auth import Unauthorized, User, validate_password
from domain.errors import Conflict
from infrastructure.models.auth_model import RecoveryModel, RefreshModel, UserModel
from infrastructure.security import tokens


class AuthService:
    def __init__(self, repository):
        self.repository = repository

    def register(self, email, password):
        validate_password(password)
        email = email.strip().lower()
        if self.repository.user(email=email):
            raise Conflict("Ese correo ya está registrado.")
        user = self.repository.add(
            UserModel(email=email, password_hash=tokens.hash_password(password))
        )
        return self.repository.identity(user)

    def login(self, email, password):
        email = email.strip().lower()
        allowed = self.repository.attempt(
            tokens.attempt_key("login", email), tokens.now(), 5
        )
        user = self.repository.user(email=email, lock=True)
        valid = tokens.verify_password(
            user.password_hash if user else tokens.dummy_hash(), password
        )
        if not allowed or not user or not user.active or not valid:
            self.repository.commit_security_event()
            raise Unauthorized(
                "Correo o contraseña incorrectos, o demasiados intentos. Si ya intentaste 5 veces, espera 15 minutos."
            )
        return self._issue(user)

    def _issue(self, user, family_id=None, expires_at=None):
        raw = secrets.token_urlsafe(48)
        self.repository.add(
            RefreshModel(
                user_id=user.id,
                family_id=family_id or uuid4(),
                token_hash=tokens.digest(raw),
                expires_at=expires_at or tokens.now() + timedelta(days=7),
            )
        )
        return tokens.encode_token(user), raw

    def current_user(self, access):
        claims = tokens.decode_token(access, "access")
        user = self.repository.user(user_id=UUID(claims["sub"]))
        if not user or not user.active or user.token_version != claims["ver"]:
            raise Unauthorized("Sesión inválida.")
        return self.repository.identity(user)

    def refresh(self, raw):
        record = self.repository.refresh(tokens.digest(raw))
        if record is None:
            raise Unauthorized("Sesión inválida.")
        user = self.repository.user(user_id=record.user_id, lock=True)
        # Releer después del bloqueo serializa refresh, logout y recuperación.
        record = self.repository.refresh(tokens.digest(raw))
        if record.used or record.revoked:
            self.repository.revoke(record.user_id, record.family_id)
            self.repository.commit_security_event()
            raise Unauthorized("Sesión inválida.")
        if not user or not user.active or record.expires_at <= tokens.now():
            raise Unauthorized("Sesión inválida.")
        record.used = True
        return self._issue(user, record.family_id, record.expires_at)

    def logout(self, raw):
        record = self.repository.refresh(tokens.digest(raw))
        if record:
            self.repository.user(user_id=record.user_id, lock=True)
            self.repository.revoke(record.user_id, record.family_id)

    def request_recovery(self, email):
        email = email.strip().lower()
        allowed = self.repository.attempt(
            tokens.attempt_key("recovery", email), tokens.now(), 3
        )
        user = self.repository.user(email=email, lock=True)
        if allowed and user and user.active:
            jti = uuid4()
            self.repository.add(
                RecoveryModel(
                    id=jti,
                    user_id=user.id,
                    expires_at=tokens.now() + timedelta(minutes=15),
                )
            )
            return tokens.encode_token(user, "recovery", jti)
        # Misma forma de respuesta para cuentas inexistentes/inactivas o limitadas.
        # Sin registro persistido, este permiso nunca puede consumirse.
        return tokens.encode_token(User(uuid4(), email, ""), "recovery", uuid4())

    def reset_password(self, token, password):
        validate_password(password)
        claims = tokens.decode_token(token, "recovery")
        user = self.repository.user(user_id=UUID(claims["sub"]), lock=True)
        record = self.repository.recovery(UUID(claims["jti"]))
        if (
            not user
            or not user.active
            or claims["ver"] != user.token_version
            or not record
            or record.user_id != user.id
            or record.used
            or record.expires_at <= tokens.now()
        ):
            raise Unauthorized(
                "El enlace no es válido, ya se usó o venció. Solicita uno nuevo con el correo de tu cuenta."
            )
        if tokens.verify_password(user.password_hash, password):
            raise ValueError("La nueva contraseña debe ser diferente de la anterior.")
        user.password_hash = tokens.hash_password(password)
        user.token_version += 1
        self.repository.invalidate_recoveries(user.id)
        self.repository.revoke(user.id)
