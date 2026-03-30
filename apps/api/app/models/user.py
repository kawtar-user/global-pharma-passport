from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.billing import Subscription
    from app.models.catalog import DrugPresentation


class UserRole(str, Enum):
    patient = "patient"
    pharmacist = "pharmacist"
    admin = "admin"


class MedicationSource(str, Enum):
    manual = "manual"
    prescription_scan = "prescription_scan"
    import_ = "import"
    api = "api"


class MedicationStatus(str, Enum):
    active = "active"
    paused = "paused"
    stopped = "stopped"


class User(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    supabase_auth_id: Mapped[str | None] = mapped_column(String(36), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="fr", nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.patient, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), unique=True)

    medications: Mapped[list["UserMedication"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserMedication(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_medications"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    drug_presentation_id: Mapped[str | None] = mapped_column(
        ForeignKey("drug_presentations.id", ondelete="SET NULL"),
        index=True,
    )
    entered_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dose_text: Mapped[str | None] = mapped_column(String(255))
    frequency_text: Mapped[str | None] = mapped_column(String(255))
    indication: Mapped[str | None] = mapped_column(Text)
    instructions_simple: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    source: Mapped[MedicationSource] = mapped_column(SqlEnum(MedicationSource), default=MedicationSource.manual)
    status: Mapped[MedicationStatus] = mapped_column(SqlEnum(MedicationStatus), default=MedicationStatus.active)

    user: Mapped["User"] = relationship(back_populates="medications")
    drug_presentation: Mapped["DrugPresentation | None"] = relationship(back_populates="user_medications")

    @property
    def presentation_summary(self) -> dict[str, object] | None:
        presentation = self.drug_presentation
        if presentation is None or presentation.drug_product is None or presentation.dosage_form is None:
            return None

        return {
            "presentation_id": str(presentation.id),
            "brand_name": presentation.drug_product.brand_name,
            "country_code": presentation.drug_product.country_code,
            "dosage_form": presentation.dosage_form.name,
            "strength_text": presentation.strength_text,
            "route": presentation.route,
            "active_ingredients": [
                item.ingredient.inn_name
                for item in presentation.ingredients
                if item.ingredient is not None
            ],
        }
