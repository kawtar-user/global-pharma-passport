import re

from pydantic import BaseModel, ConfigDict, field_validator

COUNTRY_CODE_PATTERN = re.compile(r"^[A-Z]{2}$")
LANGUAGE_CODE_PATTERN = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")


class ApiSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("*", mode="before")
    @classmethod
    def empty_strings_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value


class OrmSchema(ApiSchema):
    model_config = ConfigDict(from_attributes=True, extra="forbid", str_strip_whitespace=True)


def normalize_country_code(value: str | None) -> str | None:
    if value is None:
        return value
    normalized = value.upper()
    if not COUNTRY_CODE_PATTERN.match(normalized):
        raise ValueError("Country code must be a valid ISO alpha-2 code")
    return normalized


def normalize_language_code(value: str | None) -> str | None:
    if value is None:
        return value
    normalized = value.strip()
    if not LANGUAGE_CODE_PATTERN.match(normalized):
        raise ValueError("Language code must be a valid locale code")
    return normalized


def validate_password_strength(value: str) -> str:
    if len(value) < 10:
        raise ValueError("Password must contain at least 10 characters")
    if not any(char.isupper() for char in value):
        raise ValueError("Password must include an uppercase letter")
    if not any(char.islower() for char in value):
        raise ValueError("Password must include a lowercase letter")
    if not any(char.isdigit() for char in value):
        raise ValueError("Password must include a digit")
    if not any(not char.isalnum() for char in value):
        raise ValueError("Password must include a special character")
    return value
