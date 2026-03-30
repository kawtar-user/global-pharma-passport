from datetime import datetime

from pydantic import Field

from app.models.catalog import RiskLevel
from app.schemas.common import ApiSchema, OrmSchema


class DrugInteractionCreate(ApiSchema):
    ingredient_a_id: str
    ingredient_b_id: str
    severity: RiskLevel
    mechanism: str | None = None
    clinical_effect: str = Field(min_length=2)
    recommendation: str = Field(min_length=2)
    source_reference: str | None = Field(default=None, max_length=255)


class DrugInteractionRead(OrmSchema):
    id: str
    ingredient_a_id: str
    ingredient_b_id: str
    severity: RiskLevel
    mechanism: str | None
    clinical_effect: str
    recommendation: str
    source_reference: str | None
    created_at: datetime
    updated_at: datetime


class InteractionCheckRequest(ApiSchema):
    presentation_ids: list[str] = Field(default_factory=list, min_length=2)


class InteractionCheckMatch(ApiSchema):
    interaction_id: str
    ingredient_a_id: str
    ingredient_b_id: str
    ingredient_a_name: str
    ingredient_b_name: str
    severity: RiskLevel
    clinical_effect: str
    recommendation: str


class InteractionCheckResponse(ApiSchema):
    checked_pairs: int
    matches: list[InteractionCheckMatch]
