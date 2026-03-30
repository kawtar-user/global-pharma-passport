from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class ProductEvent(UuidPrimaryKeyMixin, Base):
    __tablename__ = "product_events"

    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    session_id: Mapped[str | None] = mapped_column(String(255))
    event_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    locale: Mapped[str | None] = mapped_column(String(10))
    country_code: Mapped[str | None] = mapped_column(String(2))
    plan_code: Mapped[str | None] = mapped_column(String(50), index=True)
    source: Mapped[str | None] = mapped_column(String(50))
    properties: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User | None"] = relationship()
