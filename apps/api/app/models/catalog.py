from __future__ import annotations

from enum import Enum

from sqlalchemy import Boolean, Enum as SqlEnum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class EquivalenceType(str, Enum):
    same_active_ingredient = "same_active_ingredient"
    same_combo = "same_combo"
    therapeutic_alternative = "therapeutic_alternative"


class RiskLevel(str, Enum):
    minor = "minor"
    moderate = "moderate"
    major = "major"
    contraindicated = "contraindicated"


class ActiveIngredient(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "active_ingredients"

    inn_name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    atc_code: Mapped[str | None] = mapped_column(String(32), index=True)
    description: Mapped[str | None] = mapped_column(Text)

    presentation_ingredients: Mapped[list["DrugPresentationIngredient"]] = relationship(back_populates="ingredient")


class DosageForm(UuidPrimaryKeyMixin, Base):
    __tablename__ = "dosage_forms"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    route: Mapped[str | None] = mapped_column(String(255))

    presentations: Mapped[list["DrugPresentation"]] = relationship(back_populates="dosage_form")


class DrugProduct(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "drug_products"

    brand_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), index=True, nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    marketing_status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    presentations: Mapped[list["DrugPresentation"]] = relationship(back_populates="drug_product", cascade="all, delete-orphan")


class DrugPresentation(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "drug_presentations"

    drug_product_id: Mapped[str] = mapped_column(ForeignKey("drug_products.id", ondelete="CASCADE"), nullable=False, index=True)
    dosage_form_id: Mapped[str] = mapped_column(ForeignKey("dosage_forms.id"), nullable=False)
    route: Mapped[str | None] = mapped_column(String(255))
    strength_text: Mapped[str] = mapped_column(String(255), nullable=False)
    package_description: Mapped[str | None] = mapped_column(String(255))
    pack_size: Mapped[int | None] = mapped_column(Integer)
    rx_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    drug_product: Mapped["DrugProduct"] = relationship(back_populates="presentations")
    dosage_form: Mapped["DosageForm"] = relationship(back_populates="presentations")
    ingredients: Mapped[list["DrugPresentationIngredient"]] = relationship(
        back_populates="drug_presentation",
        cascade="all, delete-orphan",
    )
    outgoing_equivalents: Mapped[list["DrugEquivalent"]] = relationship(
        back_populates="source_presentation",
        foreign_keys="DrugEquivalent.source_drug_presentation_id",
    )
    incoming_equivalents: Mapped[list["DrugEquivalent"]] = relationship(
        back_populates="target_presentation",
        foreign_keys="DrugEquivalent.target_drug_presentation_id",
    )
    user_medications: Mapped[list["UserMedication"]] = relationship(back_populates="drug_presentation")


class DrugPresentationIngredient(UuidPrimaryKeyMixin, Base):
    __tablename__ = "drug_presentation_ingredients"

    drug_presentation_id: Mapped[str] = mapped_column(
        ForeignKey("drug_presentations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    active_ingredient_id: Mapped[str] = mapped_column(ForeignKey("active_ingredients.id"), nullable=False, index=True)
    strength_value: Mapped[float | None] = mapped_column(Numeric(12, 4))
    strength_unit: Mapped[str | None] = mapped_column(String(64))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    drug_presentation: Mapped["DrugPresentation"] = relationship(back_populates="ingredients")
    ingredient: Mapped["ActiveIngredient"] = relationship(back_populates="presentation_ingredients")

    @property
    def active_ingredient_name(self) -> str | None:
        return self.ingredient.inn_name if self.ingredient is not None else None


class DrugEquivalent(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "drug_equivalents"

    source_drug_presentation_id: Mapped[str] = mapped_column(
        ForeignKey("drug_presentations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_drug_presentation_id: Mapped[str] = mapped_column(
        ForeignKey("drug_presentations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equivalence_type: Mapped[EquivalenceType] = mapped_column(SqlEnum(EquivalenceType), nullable=False)
    equivalence_score: Mapped[float] = mapped_column(Float, nullable=False)
    clinical_notes: Mapped[str | None] = mapped_column(Text)
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    source_presentation: Mapped["DrugPresentation"] = relationship(
        back_populates="outgoing_equivalents",
        foreign_keys=[source_drug_presentation_id],
    )
    target_presentation: Mapped["DrugPresentation"] = relationship(
        back_populates="incoming_equivalents",
        foreign_keys=[target_drug_presentation_id],
    )


class DrugInteraction(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "drug_interactions"

    ingredient_a_id: Mapped[str] = mapped_column(ForeignKey("active_ingredients.id", ondelete="CASCADE"), nullable=False)
    ingredient_b_id: Mapped[str] = mapped_column(ForeignKey("active_ingredients.id", ondelete="CASCADE"), nullable=False)
    severity: Mapped[RiskLevel] = mapped_column(SqlEnum(RiskLevel), nullable=False)
    mechanism: Mapped[str | None] = mapped_column(Text)
    clinical_effect: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(255))

    ingredient_a: Mapped["ActiveIngredient"] = relationship(foreign_keys=[ingredient_a_id])
    ingredient_b: Mapped["ActiveIngredient"] = relationship(foreign_keys=[ingredient_b_id])


from app.models.user import UserMedication  # noqa: E402
