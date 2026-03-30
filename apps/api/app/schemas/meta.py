from app.schemas.common import ApiSchema


class LanguageRead(ApiSchema):
    code: str
    name: str
    is_rtl: bool


class CountryRead(ApiSchema):
    code: str
    name: str
    default_language: str
    currency: str
    date_format: str


class RequestContextRead(ApiSchema):
    language_code: str
    country_code: str
    currency: str
    date_format: str
    is_rtl: bool
