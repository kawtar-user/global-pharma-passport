from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.config import settings
from app.models.catalog import DrugInteraction, DrugPresentation, DrugPresentationIngredient
from app.models.passport import MedicalPassport, MedicalPassportSnapshot, PassportStatus
from app.models.user import User, UserMedication
from app.schemas.passport import PassportInteractionItem, PassportMedicationItem, PassportPatientProfile, PassportSnapshotRead


def _load_user_medications(db: Session, user: User) -> list[UserMedication]:
    stmt = (
        select(UserMedication)
        .options(
            joinedload(UserMedication.drug_presentation).joinedload(DrugPresentation.drug_product),
            joinedload(UserMedication.drug_presentation).joinedload(DrugPresentation.dosage_form),
            joinedload(UserMedication.drug_presentation)
            .selectinload(DrugPresentation.ingredients)
            .joinedload(DrugPresentationIngredient.ingredient),
        )
        .where(UserMedication.user_id == user.id)
        .order_by(UserMedication.created_at.desc())
    )
    return list(db.scalars(stmt))


def _load_major_interactions(db: Session, medications: list[UserMedication]) -> list[PassportInteractionItem]:
    presentation_ids = [
        medication.drug_presentation.id
        for medication in medications
        if medication.drug_presentation is not None
    ]
    if len(presentation_ids) < 2:
        return []

    ingredient_to_medication: dict[str, set[str]] = {}
    ingredient_ids: set[str] = set()
    for medication in medications:
        presentation = medication.drug_presentation
        if presentation is None:
            continue
        for ingredient in presentation.ingredients:
            ingredient_ids.add(ingredient.active_ingredient_id)
            ingredient_to_medication.setdefault(ingredient.active_ingredient_id, set()).add(medication.id)

    if len(ingredient_ids) < 2:
        return []

    stmt = (
        select(DrugInteraction)
        .options(
            joinedload(DrugInteraction.ingredient_a),
            joinedload(DrugInteraction.ingredient_b),
        )
        .where(
            DrugInteraction.ingredient_a_id.in_(ingredient_ids),
            DrugInteraction.ingredient_b_id.in_(ingredient_ids),
            DrugInteraction.severity.in_(("major", "contraindicated")),
        )
        .order_by(DrugInteraction.severity.desc(), DrugInteraction.updated_at.desc())
    )
    interactions = list(db.scalars(stmt))

    results: list[PassportInteractionItem] = []
    for interaction in interactions:
        meds_a = ingredient_to_medication.get(interaction.ingredient_a_id, set())
        meds_b = ingredient_to_medication.get(interaction.ingredient_b_id, set())
        if not meds_a or not meds_b:
            continue
        if meds_a == meds_b and len(meds_a) == 1:
            continue
        results.append(
            PassportInteractionItem(
                interaction_id=str(interaction.id),
                severity=interaction.severity.value,
                title=f"{interaction.ingredient_a.inn_name} + {interaction.ingredient_b.inn_name}",
                clinical_effect=interaction.clinical_effect,
                recommendation=interaction.recommendation,
            )
        )
    return results


def _serialize_medication(medication: UserMedication) -> PassportMedicationItem:
    presentation = medication.drug_presentation
    if presentation is None:
        return PassportMedicationItem(
            medication_id=str(medication.id),
            entered_name=medication.entered_name,
            active_ingredients=[],
            dosage=medication.dose_text,
            frequency=medication.frequency_text,
            indication=medication.indication,
        )

    active_ingredients = [
        item.ingredient.inn_name
        for item in presentation.ingredients
        if item.ingredient is not None
    ]
    return PassportMedicationItem(
        medication_id=str(medication.id),
        entered_name=medication.entered_name,
        brand_name=presentation.drug_product.brand_name if presentation.drug_product else None,
        active_ingredients=active_ingredients,
        dosage=medication.dose_text or presentation.strength_text,
        frequency=medication.frequency_text,
        indication=medication.indication,
        country_code=presentation.drug_product.country_code if presentation.drug_product else None,
        dosage_form=presentation.dosage_form.name if presentation.dosage_form else None,
    )


def _build_snapshot_payload(user: User, medications: list[UserMedication], interactions: list[PassportInteractionItem], language_code: str) -> dict:
    serialized_medications = [_serialize_medication(medication).model_dump() for medication in medications]
    return {
        "patient": {
            "full_name": user.full_name,
            "preferred_language": user.preferred_language,
            "country_code": user.country_code,
        },
        "medications": serialized_medications,
        "major_interactions": [item.model_dump() for item in interactions],
        "language_code": language_code,
    }


def _get_or_create_passport(db: Session, user: User) -> MedicalPassport:
    passport = db.scalar(select(MedicalPassport).where(MedicalPassport.user_id == user.id))
    if passport:
        return passport

    passport = MedicalPassport(
        user_id=user.id,
        status=PassportStatus.active,
        title="Global Pharma Passport",
    )
    db.add(passport)
    db.flush()
    return passport


def _build_share_path(share_token: str) -> str:
    return f"/passport/shared/{share_token}"


def _build_share_url(language_code: str, share_token: str) -> str:
    return f"{settings.app_base_url.rstrip('/')}/{language_code}{_build_share_path(share_token)}"


def generate_passport_snapshot(db: Session, user: User, language_code: str | None = None) -> PassportSnapshotRead:
    preferred_language = language_code or user.preferred_language or "fr"
    passport = _get_or_create_passport(db, user)
    medications = _load_user_medications(db, user)
    interactions = _load_major_interactions(db, medications)
    payload = _build_snapshot_payload(user, medications, interactions, preferred_language)

    latest_version = db.scalar(
        select(MedicalPassportSnapshot.version)
        .where(
            MedicalPassportSnapshot.medical_passport_id == passport.id,
            MedicalPassportSnapshot.language_code == preferred_language,
        )
        .order_by(MedicalPassportSnapshot.version.desc())
        .limit(1)
    )
    version = (latest_version or 0) + 1

    snapshot = MedicalPassportSnapshot(
        medical_passport_id=passport.id,
        language_code=preferred_language,
        version=version,
        snapshot_json=payload,
    )
    passport.status = PassportStatus.active
    passport.last_shared_at = datetime.utcnow()
    db.add(passport)
    db.add(snapshot)
    db.commit()
    db.refresh(passport)
    db.refresh(snapshot)

    return PassportSnapshotRead(
        passport_id=str(passport.id),
        share_token=passport.share_token,
        title=passport.title,
        language_code=snapshot.language_code,
        status=passport.status,
        generated_at=snapshot.generated_at,
        share_path=_build_share_path(passport.share_token),
        share_url=_build_share_url(snapshot.language_code, passport.share_token),
        patient=PassportPatientProfile(**payload["patient"]),
        medications=[PassportMedicationItem(**item) for item in payload["medications"]],
        major_interactions=[PassportInteractionItem(**item) for item in payload["major_interactions"]],
    )


def get_shared_passport_snapshot(db: Session, share_token: str, language_code: str | None = None) -> PassportSnapshotRead:
    passport = db.scalar(
        select(MedicalPassport)
        .options(selectinload(MedicalPassport.snapshots))
        .where(MedicalPassport.share_token == share_token)
    )
    if not passport or passport.status in {PassportStatus.revoked, PassportStatus.expired}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passport not found")

    requested_language = language_code or "fr"
    matching = [item for item in passport.snapshots if item.language_code == requested_language]
    if not matching:
        matching = passport.snapshots
    if not matching:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passport snapshot not found")

    snapshot = sorted(matching, key=lambda item: item.version, reverse=True)[0]
    payload = snapshot.snapshot_json
    return PassportSnapshotRead(
        passport_id=str(passport.id),
        share_token=passport.share_token,
        title=passport.title,
        language_code=snapshot.language_code,
        status=passport.status,
        generated_at=snapshot.generated_at,
        share_path=_build_share_path(passport.share_token),
        share_url=_build_share_url(snapshot.language_code, passport.share_token),
        patient=PassportPatientProfile(**payload["patient"]),
        medications=[PassportMedicationItem(**item) for item in payload["medications"]],
        major_interactions=[PassportInteractionItem(**item) for item in payload["major_interactions"]],
    )
