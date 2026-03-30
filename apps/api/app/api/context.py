from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header

from app.core.config import settings
from app.core.international import resolve_country, resolve_language


@dataclass(frozen=True)
class RequestContext:
    language_code: str
    country_code: str
    currency: str
    date_format: str
    is_rtl: bool


def get_request_context(
    accept_language: str | None = Header(default=None, alias="Accept-Language"),
    x_country_code: str | None = Header(default=None, alias="X-Country-Code"),
) -> RequestContext:
    language = resolve_language((accept_language or settings.default_language).split(",")[0].split("-")[0].strip())
    country = resolve_country(x_country_code or settings.default_country)
    return RequestContext(
        language_code=language.code,
        country_code=country.code,
        currency=country.currency,
        date_format=country.date_format,
        is_rtl=language.is_rtl,
    )
