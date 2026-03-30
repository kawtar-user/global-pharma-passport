from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.services import billing as billing_service
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> tuple[User, str]:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        preferred_language=payload.preferred_language,
        country_code=payload.country_code.upper() if payload.country_code else None,
        role=UserRole.patient,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    billing_service.create_default_free_subscription(db, user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return user, token


def authenticate_user(db: Session, payload: LoginRequest) -> tuple[User, str]:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    token = create_access_token(user.id)
    return user, token
