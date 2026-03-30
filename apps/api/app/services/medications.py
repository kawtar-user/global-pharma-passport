from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.user import User, UserMedication
from app.services import billing as billing_service
from app.models.catalog import ActiveIngredient, DosageForm, DrugPresentation, DrugPresentationIngredient, DrugProduct
from app.schemas.medications import (
    ActiveIngredientCreate,
    DosageFormCreate,
    DrugProductCreate,
    PatientMedicationCreate,
    PatientMedicationUpdate,
)


def _patient_medication_load_options():
    return (
        joinedload(UserMedication.drug_presentation).joinedload(DrugPresentation.drug_product),
        joinedload(UserMedication.drug_presentation).joinedload(DrugPresentation.dosage_form),
        joinedload(UserMedication.drug_presentation)
        .selectinload(DrugPresentation.ingredients)
        .joinedload(DrugPresentationIngredient.ingredient),
    )


def create_active_ingredient(db: Session, payload: ActiveIngredientCreate) -> ActiveIngredient:
    existing = db.scalar(select(ActiveIngredient).where(ActiveIngredient.inn_name == payload.inn_name))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Active ingredient already exists")
    item = ActiveIngredient(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_active_ingredients(db: Session) -> list[ActiveIngredient]:
    return list(db.scalars(select(ActiveIngredient).order_by(ActiveIngredient.inn_name.asc())))


def create_dosage_form(db: Session, payload: DosageFormCreate) -> DosageForm:
    existing = db.scalar(select(DosageForm).where(DosageForm.code == payload.code))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dosage form already exists")
    item = DosageForm(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_dosage_forms(db: Session) -> list[DosageForm]:
    return list(db.scalars(select(DosageForm).order_by(DosageForm.name.asc())))


def create_drug_product(db: Session, payload: DrugProductCreate) -> DrugProduct:
    dosage_form_ids = {item.dosage_form_id for item in payload.presentations}
    known_dosage_form_ids = {
        item.id for item in db.scalars(select(DosageForm).where(DosageForm.id.in_(dosage_form_ids)))
    }
    missing_dosage_form_ids = dosage_form_ids - known_dosage_form_ids
    if missing_dosage_form_ids:
        missing_id = sorted(missing_dosage_form_ids)[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dosage form {missing_id} was not found",
        )

    product = DrugProduct(
        brand_name=payload.brand_name,
        country_code=payload.country_code.upper(),
        manufacturer=payload.manufacturer,
        marketing_status=payload.marketing_status,
        description=payload.description,
    )
    db.add(product)
    db.flush()

    for presentation_payload in payload.presentations:
        presentation = DrugPresentation(
            drug_product_id=product.id,
            dosage_form_id=presentation_payload.dosage_form_id,
            route=presentation_payload.route,
            strength_text=presentation_payload.strength_text,
            package_description=presentation_payload.package_description,
            pack_size=presentation_payload.pack_size,
            rx_required=presentation_payload.rx_required,
            is_active=presentation_payload.is_active,
        )
        db.add(presentation)
        db.flush()

        for ingredient_payload in presentation_payload.ingredients:
            ingredient = db.get(ActiveIngredient, ingredient_payload.active_ingredient_id)
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Active ingredient {ingredient_payload.active_ingredient_id} not found",
                )
            db.add(
                DrugPresentationIngredient(
                    drug_presentation_id=presentation.id,
                    active_ingredient_id=ingredient_payload.active_ingredient_id,
                    strength_value=ingredient_payload.strength_value,
                    strength_unit=ingredient_payload.strength_unit,
                    is_primary=ingredient_payload.is_primary,
                )
            )

    db.commit()
    stmt = (
        select(DrugProduct)
        .options(
            selectinload(DrugProduct.presentations).selectinload(DrugPresentation.ingredients),
        )
        .where(DrugProduct.id == product.id)
    )
    return db.scalar(stmt)


def list_drug_products(db: Session, query: str | None = None, country_code: str | None = None) -> list[DrugProduct]:
    stmt = (
        select(DrugProduct)
        .options(selectinload(DrugProduct.presentations).selectinload(DrugPresentation.ingredients))
        .order_by(DrugProduct.brand_name.asc())
    )
    if query:
        like_value = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                DrugProduct.brand_name.ilike(like_value),
                DrugProduct.description.ilike(like_value),
            )
        )
    if country_code:
        stmt = stmt.where(DrugProduct.country_code == country_code.upper())
    return list(db.scalars(stmt))


def get_drug_presentation_or_404(db: Session, presentation_id: str) -> DrugPresentation:
    stmt = (
        select(DrugPresentation)
        .options(
            joinedload(DrugPresentation.drug_product),
            joinedload(DrugPresentation.dosage_form),
            selectinload(DrugPresentation.ingredients).joinedload(DrugPresentationIngredient.ingredient),
        )
        .where(DrugPresentation.id == presentation_id)
    )
    presentation = db.scalar(stmt)
    if not presentation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drug presentation not found")
    return presentation


def list_patient_medications(db: Session, user: User) -> list[UserMedication]:
    stmt = (
        select(UserMedication)
        .options(*_patient_medication_load_options())
        .where(UserMedication.user_id == user.id)
        .order_by(UserMedication.created_at.desc())
    )
    return list(db.scalars(stmt))


def create_patient_medication(db: Session, user: User, payload: PatientMedicationCreate) -> UserMedication:
    subscription = billing_service.get_current_subscription(db, user)
    current_count = db.scalar(select(func.count(UserMedication.id)).where(UserMedication.user_id == user.id)) or 0
    billing_service.ensure_feature_access(
        plan_code=subscription.plan_code,
        feature="medications_max",
        current_value=current_count,
    )
    if payload.drug_presentation_id:
        get_drug_presentation_or_404(db, payload.drug_presentation_id)

    medication = UserMedication(user_id=user.id, **payload.model_dump())
    db.add(medication)
    db.commit()
    return get_patient_medication_or_404(db, user, medication.id)


def get_patient_medication_or_404(db: Session, user: User, medication_id: str) -> UserMedication:
    stmt = (
        select(UserMedication)
        .options(*_patient_medication_load_options())
        .where(UserMedication.id == medication_id, UserMedication.user_id == user.id)
    )
    medication = db.scalar(stmt)
    if not medication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return medication


def update_patient_medication(
    db: Session,
    user: User,
    medication_id: str,
    payload: PatientMedicationUpdate,
) -> UserMedication:
    medication = get_patient_medication_or_404(db, user, medication_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(medication, field, value)
    db.add(medication)
    db.commit()
    return get_patient_medication_or_404(db, user, medication.id)


def delete_patient_medication(db: Session, user: User, medication_id: str) -> None:
    medication = get_patient_medication_or_404(db, user, medication_id)
    db.delete(medication)
    db.commit()
