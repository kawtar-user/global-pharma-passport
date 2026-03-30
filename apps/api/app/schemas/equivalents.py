from datetime import datetime

from pydantic import Field, field_validator

from app.models.catalog import EquivalenceType
from app.schemas.common import ApiSchema, OrmSchema, normalize_country_code


class DrugEquivalentCreate(ApiSchema):
    source_drug_presentation_id: str
    target_drug_presentation_id: str
    equivalence_type: EquivalenceType
    equivalence_score: float = Field(ge=0, le=100)
    clinical_notes: str | None = None
    is_bidirectional: bool = True


class EquivalentPresentationSummary(ApiSchema):
    presentation_id: str
    brand_name: str
    country_code: str
    dosage_form: str
    strength_text: str
    route: str | None


class EquivalentSearchNotice(ApiSchema):
    code: str
    message: str


class DrugEquivalentRead(OrmSchema):
    id: str
    source_drug_presentation_id: str
    target_drug_presentation_id: str
    equivalence_type: EquivalenceType
    equivalence_score: float
    clinical_notes: str | None
    is_bidirectional: bool
    created_at: datetime
    updated_at: datetime


class EquivalentSearchResponse(ApiSchema):
    source_presentation_id: str
    target_country_code: str | None
    results: list[EquivalentPresentationSummary]
    notice: EquivalentSearchNotice | None = None

    @field_validator("target_country_code")
    @classmethod
    def validate_country_code(cls, value: str | None) -> str | None:
        return normalize_country_code(value)
