from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user, require_admin
from app.api.dependencies import get_db_session
from app.core.config import settings
from app.models.user import User
from app.schemas.analytics import AnalyticsDashboardRead, AnalyticsTrackRequest, AnalyticsTrackResponse
from app.services import analytics as analytics_service

router = APIRouter()


@router.post("/track", response_model=AnalyticsTrackResponse, status_code=status.HTTP_202_ACCEPTED)
def track_event(
    payload: AnalyticsTrackRequest,
    db: Session = Depends(get_db_session),
    current_user: User | None = Depends(get_optional_current_user),
) -> AnalyticsTrackResponse:
    if not settings.enable_product_analytics:
        return AnalyticsTrackResponse(status="disabled")
    analytics_service.track_event(db, payload=payload, user=current_user)
    return AnalyticsTrackResponse(status="accepted")


@router.get("/dashboard", response_model=AnalyticsDashboardRead)
def analytics_dashboard(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> AnalyticsDashboardRead:
    return analytics_service.build_dashboard(db)
