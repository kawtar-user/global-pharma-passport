from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, require_admin
from app.api.dependencies import get_db_session
from app.models.user import User
from app.schemas.equivalents import DrugEquivalentCreate, DrugEquivalentRead, EquivalentSearchResponse
from app.services import equivalents as equivalent_service

router = APIRouter()


@router.post("", response_model=DrugEquivalentRead, status_code=status.HTTP_201_CREATED)
def create_equivalent(
    payload: DrugEquivalentCreate,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> DrugEquivalentRead:
    return equivalent_service.create_equivalent(db, payload)


@router.get("", response_model=list[DrugEquivalentRead])
def list_equivalent_mappings(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> list[DrugEquivalentRead]:
    return equivalent_service.list_equivalent_mappings(db)


@router.get("/search/{presentation_id}", response_model=EquivalentSearchResponse)
def find_equivalents(
    presentation_id: str,
    target_country_code: str | None = Query(default=None, min_length=2, max_length=2),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> EquivalentSearchResponse:
    return equivalent_service.find_equivalents(db, current_user, presentation_id, target_country_code)
