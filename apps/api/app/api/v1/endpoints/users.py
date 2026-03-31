from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_verified_user, require_admin
from app.api.dependencies import get_db_session
from app.models.user import User
from app.schemas.users import (
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.services import users as user_service

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db_session)) -> UserRead:
    return user_service.create_user(db, payload)


@router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> list[UserRead]:
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: str,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> UserRead:
    return user_service.get_user_or_404(db, user_id)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> UserRead:
    user = user_service.get_user_or_404(db, user_id)
    return user_service.update_user(db, user, payload)


@router.get("/me/profile", response_model=UserRead)
def get_my_profile(current_user: User = Depends(get_current_verified_user)) -> UserRead:
    return current_user


@router.patch("/me/profile", response_model=UserRead)
def update_my_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_verified_user),
) -> UserRead:
    return user_service.update_user(db, current_user, payload)
