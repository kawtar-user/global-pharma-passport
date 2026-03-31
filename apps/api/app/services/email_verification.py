from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.email_verification import EmailVerificationToken
from app.models.user import User

logger = logging.getLogger("app.email_verification")


def _build_verification_url(token: str) -> str:
    return f"{settings.app_base_url.rstrip('/')}/verify-email?token={token}"


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_verification_token(db: Session, user: User) -> EmailVerificationToken:
    for existing in user.email_verification_tokens:
        if existing.consumed_at is None:
            existing.consumed_at = datetime.now(timezone.utc)
            db.add(existing)

    token = EmailVerificationToken(
        user_id=user.id,
        token=secrets.token_urlsafe(32),
        code=_generate_code(),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.email_verification_expire_hours),
    )
    db.add(token)
    db.flush()
    return token


def dispatch_verification_email(user: User, verification: EmailVerificationToken) -> None:
    verification_url = _build_verification_url(verification.token)
    logger.info(
        "email_verification_created user_id=%s email=%s code=%s verification_url=%s",
        user.id,
        user.email,
        verification.code,
        verification_url,
    )


def issue_verification(db: Session, user: User) -> EmailVerificationToken:
    verification = create_verification_token(db, user)
    dispatch_verification_email(user, verification)
    return verification


def resend_verification_for_email(db: Session, email: str) -> None:
    user = db.scalar(select(User).where(User.email == email))
    if not user or user.is_verified:
        return
    issue_verification(db, user)
    db.commit()


def confirm_email_verification(
    db: Session,
    *,
    token: str | None = None,
    email: str | None = None,
    code: str | None = None,
) -> User:
    stmt = select(EmailVerificationToken).order_by(EmailVerificationToken.created_at.desc())
    if token:
        stmt = stmt.where(EmailVerificationToken.token == token)
    elif email and code:
        stmt = (
            stmt.join(User, User.id == EmailVerificationToken.user_id)
            .where(User.email == email, EmailVerificationToken.code == code)
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token or code is required")

    verification = db.scalar(stmt)
    if not verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification request not found")
    if verification.consumed_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification request already used")
    if verification.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification request expired")

    user = db.get(User, verification.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_verified = True
    verification.consumed_at = datetime.now(timezone.utc)
    db.add(user)
    db.add(verification)
    db.commit()
    db.refresh(user)
    return user
