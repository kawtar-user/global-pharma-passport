from fastapi import APIRouter, Depends

from app.api.context import RequestContext, get_request_context
from app.core.international import SUPPORTED_COUNTRIES, SUPPORTED_LANGUAGES
from app.schemas.meta import CountryRead, LanguageRead, RequestContextRead

router = APIRouter()


@router.get("/languages", response_model=list[LanguageRead])
def list_languages() -> list[LanguageRead]:
    return [LanguageRead(**language.__dict__) for language in SUPPORTED_LANGUAGES.values()]


@router.get("/countries", response_model=list[CountryRead])
def list_countries() -> list[CountryRead]:
    return [CountryRead(**country.__dict__) for country in SUPPORTED_COUNTRIES.values()]


@router.get("/request-context", response_model=RequestContextRead)
def get_context(context: RequestContext = Depends(get_request_context)) -> RequestContextRead:
    return RequestContextRead(**context.__dict__)
