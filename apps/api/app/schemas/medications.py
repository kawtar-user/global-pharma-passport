from datetime import datetime

from pydantic import Field, field_validator

from app.models.user import MedicationStatus
from app.schemas.common import ApiSchema, OrmSchema, normalize_country_code


class ActiveIngredientCreate(ApiSchema):
    inn_name: str = Field(min_length=2, max_length=255)
    atc_code: str | None = Field(default=None, max_length=32)
    description: str | None = None


class ActiveIngredientRead(OrmSchema):
    id: str
    inn_name: str
    atc_code: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class DosageFormCreate(ApiSchema):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=255)
    route: str | None = Field(default=None, max_length=255)


class DosageFormRead(OrmSchema):
    id: str
    code: str
    name: str
    route: str | None


class MedicationIngredientInput(ApiSchema):
    active_ingredient_id: str
    strength_value: float | None = Field(default=None, gt=0)
    strength_unit: str | None = Field(default=None, max_length=64)
    is_primary: bool = False


class DrugPresentationCreate(ApiSchema):
    dosage_form_id: str
    route: str | None = Field(default=None, max_length=255)
    strength_text: str = Field(min_length=1, max_length=255)
    package_description: str | None = Field(default=None, max_length=255)
    pack_size: int | None = Field(default=None, gt=0)
    rx_required: bool = True
    is_active: bool = True
    ingredients: list[MedicationIngredientInput] = Field(default_factory=list, min_length=1)


class DrugProductCreate(ApiSchema):
    brand_name: str = Field(min_length=2, max_length=255)
    country_code: str = Field(min_length=2, max_length=2)
    manufacturer: str | None = Field(default=None, max_length=255)
    marketing_status: str = Field(default="active", max_length=50)
    description: str | None = None
    presentations: list[DrugPresentationCreate] = Field(default_factory=list, min_length=1)

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, value: str) -> str:
        normalized = normalize_country_code(value)
        assert normalized is not None
        return normalized


class MedicationIngredientRead(OrmSchema):
    id: str
    active_ingredient_id: str
    active_ingredient_name: str | None = None
    strength_value: float | None
    strength_unit: str | None
    is_primary: bool


class MedicationPresentationSummary(ApiSchema):
    presentation_id: str
    brand_name: str
    country_code: str
    dosage_form: str
    strength_text: str
    route: str | None
    active_ingredients: list[str] = Field(default_factory=list)


class DrugPresentationRead(OrmSchema):
    id: str
    drug_product_id: str
    dosage_form_id: str
    route: str | None
    strength_text: str
    package_description: str | None
    pack_size: int | None
    rx_required: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    ingredients: list[MedicationIngredientRead]


class DrugProductRead(OrmSchema):
    id: str
    brand_name: str
    country_code: str
    manufacturer: str | None
    marketing_status: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    presentations: list[DrugPresentationRead]


class MedicationSearchResult(OrmSchema):
    id: str
    brand_name: str
    country_code: str
    manufacturer: str | None
    marketing_status: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class PatientMedicationCreate(ApiSchema):
    drug_presentation_id: str | None = None
    entered_name: str = Field(min_length=2, max_length=255)
    dose_text: str | None = Field(default=None, max_length=255)
    frequency_text: str | None = Field(default=None, max_length=255)
    indication: str | None = None
    instructions_simple: str | None = None
    status: MedicationStatus = MedicationStatus.active


class PatientMedicationUpdate(ApiSchema):
    entered_name: str | None = Field(default=None, min_length=2, max_length=255)
    dose_text: str | None = Field(default=None, max_length=255)
    frequency_text: str | None = Field(default=None, max_length=255)
    indication: str | None = None
    instructions_simple: str | None = None
    status: MedicationStatus | None = None


class PatientMedicationRead(OrmSchema):
    id: str
    user_id: str
    drug_presentation_id: str | None
    entered_name: str
    dose_text: str | None
    frequency_text: str | None
    indication: str | None
    instructions_simple: str | None
    status: MedicationStatus
    created_at: datetime
    updated_at: datetime
    presentation_summary: MedicationPresentationSummary | None = None
