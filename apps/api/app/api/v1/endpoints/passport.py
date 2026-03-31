from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_verified_user
from app.api.dependencies import get_db_session
from app.models.user import User
from app.schemas.passport import PassportSnapshotRead
from app.services import passport as passport_service

router = APIRouter()


@router.get("/me", response_model=PassportSnapshotRead)
def get_my_passport(
    language_code: str | None = Query(default=None, min_length=2, max_length=10),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_verified_user),
) -> PassportSnapshotRead:
    return passport_service.generate_passport_snapshot(db, current_user, language_code)


@router.get("/shared/{share_token}", response_model=PassportSnapshotRead)
def get_shared_passport(
    share_token: str,
    language_code: str | None = Query(default=None, min_length=2, max_length=10),
    db: Session = Depends(get_db_session),
) -> PassportSnapshotRead:
    return passport_service.get_shared_passport_snapshot(db, share_token, language_code)
