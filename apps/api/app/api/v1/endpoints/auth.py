from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.dependencies import get_db_session
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    AuthenticatedUserRead,
    EmailVerificationConfirmRequest,
    EmailVerificationRequest,
    EmailVerificationResponse,
    LoginRequest,
    RegisterRequest,
)
from app.services import auth as auth_service
from app.services import email_verification as email_verification_service

router = APIRouter()


@router.post("/register", response_model=AccessTokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db_session),
) -> AccessTokenResponse:
    response.headers["Cache-Control"] = "no-store"
    _, token = auth_service.register_user(db, payload)
    return AccessTokenResponse(access_token=token, requires_verification=True)


@router.post("/login", response_model=AccessTokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db_session),
) -> AccessTokenResponse:
    response.headers["Cache-Control"] = "no-store"
    user, token = auth_service.authenticate_user(db, payload)
    return AccessTokenResponse(access_token=token, requires_verification=not user.is_verified)


@router.get("/me", response_model=AuthenticatedUserRead)
def me(current_user: User = Depends(get_current_user)) -> AuthenticatedUserRead:
    return AuthenticatedUserRead(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        preferred_language=current_user.preferred_language,
        country_code=current_user.country_code,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/verify-email/request", response_model=EmailVerificationResponse)
def request_email_verification(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db_session),
) -> EmailVerificationResponse:
    email_verification_service.resend_verification_for_email(db, payload.email)
    return EmailVerificationResponse(
        message="If the account exists and is not verified, a confirmation email has been sent.",
        verification_required=True,
    )


@router.post("/verify-email/confirm", response_model=EmailVerificationResponse)
def confirm_email_verification(
    payload: EmailVerificationConfirmRequest,
    db: Session = Depends(get_db_session),
) -> EmailVerificationResponse:
    email_verification_service.confirm_email_verification(
        db,
        token=payload.token,
        email=payload.email,
        code=payload.code,
    )
    return EmailVerificationResponse(
        message="Email verified successfully. The account is now active.",
        verification_required=False,
    )


@router.get("/verify-email/confirm", response_model=EmailVerificationResponse)
def confirm_email_verification_from_link(
    token: str = Query(..., min_length=16),
    db: Session = Depends(get_db_session),
) -> EmailVerificationResponse:
    email_verification_service.confirm_email_verification(db, token=token)
    return EmailVerificationResponse(
        message="Email verified successfully. The account is now active.",
        verification_required=False,
    )
