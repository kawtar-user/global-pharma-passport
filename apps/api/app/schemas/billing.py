from datetime import datetime

from pydantic import Field

from app.models.billing import SubscriptionStatus
from app.schemas.common import ApiSchema, OrmSchema


class PlanLimits(ApiSchema):
    medications_max: int | None
    equivalent_results_per_search: int | None
    travel_mode_enabled: bool


class SubscriptionRead(OrmSchema):
    id: str
    user_id: str | None
    plan_code: str
    status: SubscriptionStatus
    provider: str
    provider_subscription_id: str | None
    provider_price_id: str | None
    current_period_start: datetime | None
    current_period_end: datetime | None
    trial_ends_at: datetime | None
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime


class EntitlementRead(ApiSchema):
    plan_code: str
    limits: PlanLimits
    is_premium: bool


class CheckoutSessionRequest(ApiSchema):
    success_path: str = Field(default="/billing/success", pattern=r"^/[A-Za-z0-9/_-]*$")
    cancel_path: str = Field(default="/billing/cancel", pattern=r"^/[A-Za-z0-9/_-]*$")


class CheckoutSessionResponse(ApiSchema):
    checkout_url: str


class BillingPortalResponse(ApiSchema):
    portal_url: str
