from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

from domain.auth import validate_password


class LoginDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=128)


class RegisterDTO(LoginDTO):
    @field_validator("password")
    @classmethod
    def password_policy(cls, value):
        validate_password(value.get_secret_value())
        return value


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    role: Literal["lector", "admin"]
    active: bool


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class RecoveryDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr


class ResetDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: SecretStr | None = Field(default=None, min_length=1, max_length=4096)
    password: SecretStr = Field(min_length=12, max_length=128)


class MessageDTO(BaseModel):
    message: str


class RecoveryResponseDTO(BaseModel):
    message: str
    reset_link: str
