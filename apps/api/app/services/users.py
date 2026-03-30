from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.services import billing as billing_service
from app.schemas.users import UserCreate, UserUpdate


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    requested_role = payload.role
    if requested_role != UserRole.patient:
        user_count = db.scalar(select(func.count(User.id))) or 0
        bootstrap_admin_allowed = not settings.is_production and user_count == 0
        if not bootstrap_admin_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Creating elevated roles is not allowed from this endpoint",
            )

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        preferred_language=payload.preferred_language,
        country_code=payload.country_code.upper() if payload.country_code else None,
        role=requested_role,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    billing_service.create_default_free_subscription(db, user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc())
    return list(db.scalars(stmt))


def get_user_or_404(db: Session, user_id: str) -> User:
    stmt = select(User).options(selectinload(User.medications)).where(User.id == user_id)
    user = db.scalar(stmt)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "country_code" and value is not None:
            value = value.upper()
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
