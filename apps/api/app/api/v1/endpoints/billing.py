from __future__ import annotations

import json

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.dependencies import get_db_session
from app.core.config import settings
from app.models.user import User
from app.schemas.billing import (
    BillingPortalResponse,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    EntitlementRead,
    SubscriptionRead,
)
from app.services import billing as billing_service

router = APIRouter()


@router.get("/me/subscription", response_model=SubscriptionRead)
def get_my_subscription(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> SubscriptionRead:
    return billing_service.get_current_subscription(db, current_user)


@router.get("/me/entitlements", response_model=EntitlementRead)
def get_my_entitlements(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> EntitlementRead:
    subscription = billing_service.get_current_subscription(db, current_user)
    return EntitlementRead(**billing_service.build_entitlements(subscription))


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    payload: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
) -> CheckoutSessionResponse:
    return CheckoutSessionResponse(
        checkout_url=billing_service.create_checkout_session(
            current_user,
            success_path=payload.success_path,
            cancel_path=payload.cancel_path,
        )
    )


@router.post("/portal-session", response_model=BillingPortalResponse)
def create_portal_session(current_user: User = Depends(get_current_user)) -> BillingPortalResponse:
    return BillingPortalResponse(portal_url=billing_service.create_billing_portal_session(current_user))


@router.post("/webhooks/stripe", status_code=status.HTTP_204_NO_CONTENT)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db_session),
) -> None:
    payload = await request.body()
    if settings.stripe_webhook_secret and stripe_signature:
        try:
            event = stripe.Webhook.construct_event(payload=payload, sig_header=stripe_signature, secret=settings.stripe_webhook_secret)
        except stripe.error.SignatureVerificationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe signature") from exc
    else:
        event = json.loads(payload.decode("utf-8"))

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})
    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        if user_id:
            billing_service.sync_subscription_from_checkout(
                db,
                user_id=user_id,
                stripe_customer_id=data.get("customer"),
                stripe_subscription_id=data.get("subscription"),
            )
