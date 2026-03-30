from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, require_admin
from app.api.dependencies import get_db_session
from app.models.user import User
from app.schemas.interactions import (
    DrugInteractionCreate,
    DrugInteractionRead,
    InteractionCheckRequest,
    InteractionCheckResponse,
)
from app.services import interactions as interaction_service

router = APIRouter()


@router.post("", response_model=DrugInteractionRead, status_code=status.HTTP_201_CREATED)
def create_interaction(
    payload: DrugInteractionCreate,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> DrugInteractionRead:
    return interaction_service.create_interaction(db, payload)


@router.get("", response_model=list[DrugInteractionRead])
def list_interactions(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> list[DrugInteractionRead]:
    return interaction_service.list_interactions(db)


@router.post("/check", response_model=InteractionCheckResponse)
def check_interactions(
    payload: InteractionCheckRequest,
    db: Session = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> InteractionCheckResponse:
    return interaction_service.check_interactions(db, payload.presentation_ids)
