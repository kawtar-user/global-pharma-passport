from datetime import date

from pydantic import Field, field_validator

from app.schemas.common import ApiSchema, OrmSchema, normalize_country_code, normalize_language_code


class AnalyticsTrackRequest(ApiSchema):
    event_name: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9_]+$")
    session_id: str | None = Field(default=None, max_length=255)
    locale: str | None = Field(default=None, max_length=10)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    source: str | None = Field(default="web", max_length=50)
    properties: dict[str, str | int | float | bool | None] = Field(default_factory=dict)

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, value: str | None) -> str | None:
        return normalize_country_code(value)

    @field_validator("locale")
    @classmethod
    def validate_locale(cls, value: str | None) -> str | None:
        return normalize_language_code(value)


class AnalyticsTrackResponse(ApiSchema):
    status: str


class AnalyticsMetricRead(ApiSchema):
    label: str
    value: int | float


class FeatureUsageRead(ApiSchema):
    event_name: str
    count: int


class AnalyticsDashboardRead(ApiSchema):
    total_users: int
    active_users_7d: int
    retained_users_7d: int
    free_to_paid_conversions: int
    feature_usage: list[FeatureUsageRead]
    metrics: list[AnalyticsMetricRead]


class AnalyticsEventRead(OrmSchema):
    id: str
    user_id: str | None
    session_id: str | None
    event_name: str
    locale: str | None
    country_code: str | None
    plan_code: str | None
    source: str | None
    occurred_at: date
