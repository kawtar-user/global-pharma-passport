from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.analytics import ProductEvent
from app.models.billing import Subscription
from app.models.user import User
from app.schemas.analytics import AnalyticsDashboardRead, FeatureUsageRead
from app.schemas.analytics import AnalyticsTrackRequest
from app.services import billing as billing_service

SENSITIVE_PROPERTY_KEYS = {
    "email",
    "password",
    "full_name",
    "medication_name",
    "entered_name",
    "ocr_text",
    "notes",
    "token",
}


def _sanitize_properties(properties: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in properties.items():
        normalized_key = key.lower().strip()
        if normalized_key in SENSITIVE_PROPERTY_KEYS:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            sanitized[normalized_key] = value
    return sanitized


def track_event(
    db: Session,
    *,
    payload: AnalyticsTrackRequest,
    user: User | None = None,
) -> ProductEvent:
    plan_code = None
    if user:
        plan_code = billing_service.get_current_subscription(db, user).plan_code

    event = ProductEvent(
        user_id=user.id if user else None,
        session_id=payload.session_id,
        event_name=payload.event_name,
        locale=payload.locale,
        country_code=payload.country_code,
        plan_code=plan_code,
        source=payload.source,
        properties=_sanitize_properties(payload.properties),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def build_dashboard(db: Session) -> AnalyticsDashboardRead:
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)

    total_users = db.scalar(select(func.count(User.id))) or 0
    active_users_7d = db.scalar(
        select(func.count(distinct(ProductEvent.user_id))).where(
            ProductEvent.user_id.is_not(None),
            ProductEvent.occurred_at >= seven_days_ago,
        )
    ) or 0

    previous_period_users = (
        select(ProductEvent.user_id)
        .where(
            ProductEvent.user_id.is_not(None),
            ProductEvent.occurred_at >= fourteen_days_ago,
            ProductEvent.occurred_at < seven_days_ago,
        )
        .group_by(ProductEvent.user_id)
        .subquery()
    )
    current_period_users = (
        select(ProductEvent.user_id)
        .where(
            ProductEvent.user_id.is_not(None),
            ProductEvent.occurred_at >= seven_days_ago,
        )
        .group_by(ProductEvent.user_id)
        .subquery()
    )
    retained_users_7d = db.scalar(
        select(func.count())
        .select_from(previous_period_users)
        .join(current_period_users, previous_period_users.c.user_id == current_period_users.c.user_id)
    ) or 0

    free_to_paid_conversions = db.scalar(
        select(func.count(distinct(Subscription.user_id))).where(
            Subscription.plan_code == billing_service.PREMIUM_PLAN,
            Subscription.user_id.is_not(None),
        )
    ) or 0

    feature_rows = db.execute(
        select(ProductEvent.event_name, func.count(ProductEvent.id).label("count"))
        .group_by(ProductEvent.event_name)
        .order_by(func.count(ProductEvent.id).desc())
        .limit(10)
    ).all()

    feature_usage = [
        FeatureUsageRead(event_name=row.event_name, count=row.count)
        for row in feature_rows
    ]

    metrics = [
        {"label": "Total users", "value": int(total_users)},
        {"label": "Active users (7d)", "value": int(active_users_7d)},
        {"label": "Returning users (prev 7d cohort)", "value": int(retained_users_7d)},
        {"label": "Free to paid conversions", "value": int(free_to_paid_conversions)},
    ]

    return AnalyticsDashboardRead(
        total_users=int(total_users),
        active_users_7d=int(active_users_7d),
        retained_users_7d=int(retained_users_7d),
        free_to_paid_conversions=int(free_to_paid_conversions),
        feature_usage=feature_usage,
        metrics=metrics,
    )
