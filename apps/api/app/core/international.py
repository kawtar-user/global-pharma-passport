from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageDefinition:
    code: str
    name: str
    is_rtl: bool


@dataclass(frozen=True)
class CountryDefinition:
    code: str
    name: str
    default_language: str
    currency: str
    date_format: str


SUPPORTED_LANGUAGES: dict[str, LanguageDefinition] = {
    "fr": LanguageDefinition(code="fr", name="French", is_rtl=False),
    "en": LanguageDefinition(code="en", name="English", is_rtl=False),
    "ar": LanguageDefinition(code="ar", name="Arabic", is_rtl=True),
}

SUPPORTED_COUNTRIES: dict[str, CountryDefinition] = {
    "MA": CountryDefinition(code="MA", name="Morocco", default_language="fr", currency="MAD", date_format="DD/MM/YYYY"),
    "FR": CountryDefinition(code="FR", name="France", default_language="fr", currency="EUR", date_format="DD/MM/YYYY"),
    "GB": CountryDefinition(code="GB", name="United Kingdom", default_language="en", currency="GBP", date_format="DD/MM/YYYY"),
    "US": CountryDefinition(code="US", name="United States", default_language="en", currency="USD", date_format="MM/DD/YYYY"),
}


def resolve_language(code: str | None) -> LanguageDefinition:
    return SUPPORTED_LANGUAGES.get((code or "").lower(), SUPPORTED_LANGUAGES["fr"])


def resolve_country(code: str | None) -> CountryDefinition:
    return SUPPORTED_COUNTRIES.get((code or "").upper(), SUPPORTED_COUNTRIES["MA"])
