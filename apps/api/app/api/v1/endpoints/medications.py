from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, require_admin
from app.api.dependencies import get_db_session
from app.models.user import User
from app.schemas.medications import (
    ActiveIngredientCreate,
    ActiveIngredientRead,
    DosageFormCreate,
    DosageFormRead,
    DrugProductCreate,
    DrugProductRead,
    PatientMedicationCreate,
    PatientMedicationRead,
    PatientMedicationUpdate,
)
from app.services import medications as medication_service

router = APIRouter()


def _serialize_product(product) -> DrugProductRead:
    return DrugProductRead.model_validate(product)


def _serialize_patient_medication(medication) -> PatientMedicationRead:
    return PatientMedicationRead.model_validate(medication)


@router.post("/ingredients", response_model=ActiveIngredientRead, status_code=status.HTTP_201_CREATED)
def create_active_ingredient(
    payload: ActiveIngredientCreate,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> ActiveIngredientRead:
    return medication_service.create_active_ingredient(db, payload)


@router.get("/ingredients", response_model=list[ActiveIngredientRead])
def list_active_ingredients(db: Session = Depends(get_db_session)) -> list[ActiveIngredientRead]:
    return medication_service.list_active_ingredients(db)


@router.post("/dosage-forms", response_model=DosageFormRead, status_code=status.HTTP_201_CREATED)
def create_dosage_form(
    payload: DosageFormCreate,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> DosageFormRead:
    return medication_service.create_dosage_form(db, payload)


@router.get("/dosage-forms", response_model=list[DosageFormRead])
def list_dosage_forms(db: Session = Depends(get_db_session)) -> list[DosageFormRead]:
    return medication_service.list_dosage_forms(db)


@router.post("/products", response_model=DrugProductRead, status_code=status.HTTP_201_CREATED)
def create_drug_product(
    payload: DrugProductCreate,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> DrugProductRead:
    return medication_service.create_drug_product(db, payload)


@router.get("/products", response_model=list[DrugProductRead])
def list_drug_products(
    query: str | None = Query(default=None, min_length=2),
    country_code: str | None = Query(default=None, min_length=2, max_length=2),
    db: Session = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[DrugProductRead]:
    return [
        _serialize_product(item)
        for item in medication_service.list_drug_products(db, query=query, country_code=country_code)
    ]


@router.get("/me", response_model=list[PatientMedicationRead])
def list_my_medications(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[PatientMedicationRead]:
    return [
        _serialize_patient_medication(item)
        for item in medication_service.list_patient_medications(db, current_user)
    ]


@router.post("/me", response_model=PatientMedicationRead, status_code=status.HTTP_201_CREATED)
def create_my_medication(
    payload: PatientMedicationCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PatientMedicationRead:
    return _serialize_patient_medication(
        medication_service.create_patient_medication(db, current_user, payload)
    )


@router.patch("/me/{medication_id}", response_model=PatientMedicationRead)
def update_my_medication(
    medication_id: str,
    payload: PatientMedicationUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PatientMedicationRead:
    return _serialize_patient_medication(
        medication_service.update_patient_medication(db, current_user, medication_id, payload)
    )


@router.delete("/me/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_medication(
    medication_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    medication_service.delete_patient_medication(db, current_user, medication_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
