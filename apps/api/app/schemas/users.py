from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from app.models.user import UserRole
from app.schemas.common import ApiSchema, OrmSchema, normalize_country_code, normalize_language_code, validate_password_strength


class UserCreate(ApiSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    preferred_language: str = Field(default="fr", min_length=2, max_length=10)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    role: UserRole = UserRole.patient

    _validate_password = field_validator("password")(validate_password_strength)

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, value: str | None) -> str | None:
        return normalize_country_code(value)

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        normalized = normalize_language_code(value)
        assert normalized is not None
        return normalized


class UserUpdate(ApiSchema):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    preferred_language: str | None = Field(default=None, min_length=2, max_length=10)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    role: UserRole | None = None

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, value: str | None) -> str | None:
        return normalize_country_code(value)

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str | None) -> str | None:
        return normalize_language_code(value)


class UserRead(OrmSchema):
    id: str
    email: EmailStr
    full_name: str
    preferred_language: str
    country_code: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
