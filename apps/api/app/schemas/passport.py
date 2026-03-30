from datetime import datetime

from app.models.passport import PassportStatus
from app.schemas.common import ApiSchema


class PassportPatientProfile(ApiSchema):
    full_name: str
    preferred_language: str
    country_code: str | None = None


class PassportMedicationItem(ApiSchema):
    medication_id: str
    entered_name: str
    brand_name: str | None = None
    active_ingredients: list[str]
    dosage: str | None = None
    frequency: str | None = None
    indication: str | None = None
    country_code: str | None = None
    dosage_form: str | None = None


class PassportInteractionItem(ApiSchema):
    interaction_id: str
    severity: str
    title: str
    clinical_effect: str
    recommendation: str


class PassportSnapshotRead(ApiSchema):
    passport_id: str
    share_token: str
    title: str
    language_code: str
    status: PassportStatus
    generated_at: datetime
    share_path: str
    share_url: str
    patient: PassportPatientProfile
    medications: list[PassportMedicationItem]
    major_interactions: list[PassportInteractionItem]
