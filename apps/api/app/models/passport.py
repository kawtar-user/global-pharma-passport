from __future__ import annotations

from datetime import datetime
import uuid
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class PassportStatus(str, Enum):
    draft = "draft"
    active = "active"
    revoked = "revoked"
    expired = "expired"


class MedicalPassport(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "medical_passports"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    share_token: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    status: Mapped[PassportStatus] = mapped_column(SqlEnum(PassportStatus), default=PassportStatus.draft, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="Global Pharma Passport")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_shared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    snapshots: Mapped[list["MedicalPassportSnapshot"]] = relationship(
        back_populates="passport",
        cascade="all, delete-orphan",
    )


class MedicalPassportSnapshot(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "medical_passport_snapshots"
    __table_args__ = (
        UniqueConstraint("medical_passport_id", "language_code", "version", name="medical_passport_snapshots_unique"),
    )

    medical_passport_id: Mapped[str] = mapped_column(
        ForeignKey("medical_passports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    passport: Mapped["MedicalPassport"] = relationship(back_populates="snapshots")
