from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import stripe
from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.billing import Subscription, SubscriptionStatus
from app.models.user import User


@dataclass(frozen=True)
class PlanLimitSet:
    medications_max: int | None
    equivalent_results_per_search: int | None
    travel_mode_enabled: bool


FREE_PLAN = "free"
PREMIUM_PLAN = "premium"

PLAN_LIMITS: dict[str, PlanLimitSet] = {
    FREE_PLAN: PlanLimitSet(medications_max=3, equivalent_results_per_search=1, travel_mode_enabled=False),
    PREMIUM_PLAN: PlanLimitSet(medications_max=None, equivalent_results_per_search=None, travel_mode_enabled=True),
}


def create_default_free_subscription(db: Session, user: User) -> Subscription:
    if user.id is None:
        db.flush()
    subscription = Subscription(
        user_id=user.id,
        plan_code=FREE_PLAN,
        status=SubscriptionStatus.active,
        provider="system",
        current_period_start=datetime.now(timezone.utc),
    )
    db.add(subscription)
    db.flush()
    return subscription


def get_current_subscription(db: Session, user: User) -> Subscription:
    stmt = (
        select(Subscription)
        .where(Subscription.user_id == user.id)
        .order_by(desc(Subscription.created_at))
    )
    subscription = db.scalar(stmt)
    if subscription:
        return subscription
    subscription = create_default_free_subscription(db, user)
    db.commit()
    db.refresh(subscription)
    return subscription


def get_plan_limits(plan_code: str) -> PlanLimitSet:
    return PLAN_LIMITS.get(plan_code, PLAN_LIMITS[FREE_PLAN])


def ensure_feature_access(
    *,
    plan_code: str,
    feature: str,
    current_value: int | None = None,
) -> None:
    limits = get_plan_limits(plan_code)
    if feature == "medications_max" and limits.medications_max is not None and current_value is not None:
        if current_value >= limits.medications_max:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Free plan limit reached. Upgrade to Premium for more medications.",
            )


def build_entitlements(subscription: Subscription) -> dict:
    limits = get_plan_limits(subscription.plan_code)
    return {
        "plan_code": subscription.plan_code,
        "limits": {
            "medications_max": limits.medications_max,
            "equivalent_results_per_search": limits.equivalent_results_per_search,
            "travel_mode_enabled": limits.travel_mode_enabled,
        },
        "is_premium": subscription.plan_code == PREMIUM_PLAN and subscription.status in {
            SubscriptionStatus.active,
            SubscriptionStatus.trialing,
        },
    }


def _configure_stripe() -> None:
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured yet",
        )
    stripe.api_key = settings.stripe_secret_key


def create_checkout_session(user: User, *, success_path: str, cancel_path: str) -> str:
    _configure_stripe()
    if not settings.stripe_premium_monthly_price_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe price is not configured")

    session = stripe.checkout.Session.create(
        mode="subscription",
        success_url=f"{settings.app_base_url}{success_path}",
        cancel_url=f"{settings.app_base_url}{cancel_path}",
        customer_email=user.email,
        line_items=[{"price": settings.stripe_premium_monthly_price_id, "quantity": 1}],
        metadata={"user_id": user.id, "plan_code": PREMIUM_PLAN},
    )
    return str(session.url)


def create_billing_portal_session(user: User) -> str:
    _configure_stripe()
    if not user.stripe_customer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Stripe customer linked to this user")
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{settings.app_base_url}/dashboard",
    )
    return str(session.url)


def sync_subscription_from_checkout(
    db: Session,
    *,
    user_id: str,
    stripe_customer_id: str | None,
    stripe_subscription_id: str | None,
) -> Subscription:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id

    subscription = get_current_subscription(db, user)
    subscription.plan_code = PREMIUM_PLAN
    subscription.status = SubscriptionStatus.active
    subscription.provider = "stripe"
    subscription.provider_subscription_id = stripe_subscription_id
    subscription.provider_price_id = settings.stripe_premium_monthly_price_id
    subscription.current_period_start = datetime.now(timezone.utc)

    db.add(user)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription
