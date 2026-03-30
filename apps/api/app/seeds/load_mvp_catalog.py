from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import SessionLocal
from app.models.catalog import (
    ActiveIngredient,
    DosageForm,
    DrugEquivalent,
    DrugInteraction,
    DrugPresentation,
    DrugPresentationIngredient,
    DrugProduct,
)
from app.seeds.mvp_maroc_france import ACTIVE_INGREDIENTS, DATASET_NAME, DOSAGE_FORMS, EQUIVALENTS, INTERACTIONS, PRODUCTS


def _ordered_pair(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def ensure_dosage_form(db: Session, payload: dict) -> DosageForm:
    existing = db.scalar(select(DosageForm).where(DosageForm.code == payload["code"]))
    if existing:
        existing.name = payload["name"]
        existing.route = payload["route"]
        db.add(existing)
        db.flush()
        return existing

    item = DosageForm(code=payload["code"], name=payload["name"], route=payload["route"])
    db.add(item)
    db.flush()
    return item


def ensure_active_ingredient(db: Session, payload: dict) -> ActiveIngredient:
    existing = db.scalar(select(ActiveIngredient).where(ActiveIngredient.inn_name == payload["inn_name"]))
    if existing:
        if payload["atc_code"]:
            existing.atc_code = payload["atc_code"]
        db.add(existing)
        db.flush()
        return existing

    item = ActiveIngredient(
        inn_name=payload["inn_name"],
        atc_code=payload["atc_code"],
        description=f"{DATASET_NAME} seed ingredient",
    )
    db.add(item)
    db.flush()
    return item


def _load_product(db: Session, brand_name: str, country_code: str) -> DrugProduct | None:
    stmt = (
        select(DrugProduct)
        .options(
            selectinload(DrugProduct.presentations).selectinload(DrugPresentation.ingredients),
            selectinload(DrugProduct.presentations).joinedload(DrugPresentation.dosage_form),
        )
        .where(
            DrugProduct.brand_name == brand_name,
            DrugProduct.country_code == country_code,
        )
    )
    return db.scalar(stmt)


def ensure_product(db: Session, payload: dict, dosage_forms: dict[str, DosageForm], ingredients: dict[str, ActiveIngredient]) -> DrugPresentation:
    product = _load_product(db, payload["brand_name"], payload["country_code"])
    if product is None:
        product = DrugProduct(
            brand_name=payload["brand_name"],
            country_code=payload["country_code"],
            manufacturer=payload["manufacturer"],
            marketing_status="active",
            description=payload["description"],
        )
        db.add(product)
        db.flush()
    else:
        product.manufacturer = payload["manufacturer"]
        product.description = payload["description"]
        db.add(product)
        db.flush()

    presentation_payload = payload["presentation"]
    dosage_form = dosage_forms[presentation_payload["dosage_form_code"]]

    for presentation in product.presentations:
        if (
            presentation.dosage_form_id == dosage_form.id
            and presentation.strength_text == presentation_payload["strength_text"]
            and presentation.route == presentation_payload["route"]
        ):
            return presentation

    presentation = DrugPresentation(
        drug_product_id=product.id,
        dosage_form_id=dosage_form.id,
        route=presentation_payload["route"],
        strength_text=presentation_payload["strength_text"],
        rx_required=True,
        is_active=True,
    )
    db.add(presentation)
    db.flush()

    for ingredient_payload in presentation_payload["ingredients"]:
        db.add(
            DrugPresentationIngredient(
                drug_presentation_id=presentation.id,
                active_ingredient_id=ingredients[ingredient_payload["inn_name"]].id,
                strength_value=ingredient_payload["strength_value"],
                strength_unit=ingredient_payload["strength_unit"],
                is_primary=ingredient_payload["is_primary"],
            )
        )

    db.flush()
    return presentation


def ensure_equivalent(db: Session, payload: dict, presentation_ids: dict[str, str]) -> None:
    source_id = presentation_ids[payload["source_key"]]
    target_id = presentation_ids[payload["target_key"]]

    existing = db.scalar(
        select(DrugEquivalent).where(
            DrugEquivalent.source_drug_presentation_id == source_id,
            DrugEquivalent.target_drug_presentation_id == target_id,
            DrugEquivalent.equivalence_type == payload["equivalence_type"],
        )
    )
    if existing:
        existing.equivalence_score = payload["equivalence_score"]
        existing.clinical_notes = payload["clinical_notes"]
        existing.is_bidirectional = True
        db.add(existing)
        db.flush()
        return

    db.add(
        DrugEquivalent(
            source_drug_presentation_id=source_id,
            target_drug_presentation_id=target_id,
            equivalence_type=payload["equivalence_type"],
            equivalence_score=payload["equivalence_score"],
            clinical_notes=payload["clinical_notes"],
            is_bidirectional=True,
        )
    )
    db.flush()


def ensure_interaction(db: Session, payload: dict, ingredients: dict[str, ActiveIngredient]) -> None:
    ingredient_a_id, ingredient_b_id = _ordered_pair(
        ingredients[payload["ingredient_a"]].id,
        ingredients[payload["ingredient_b"]].id,
    )
    existing = db.scalar(
        select(DrugInteraction).where(
            DrugInteraction.ingredient_a_id == ingredient_a_id,
            DrugInteraction.ingredient_b_id == ingredient_b_id,
        )
    )
    if existing:
        existing.severity = payload["severity"]
        existing.clinical_effect = payload["clinical_effect"]
        existing.recommendation = payload["recommendation"]
        existing.source_reference = payload["source_reference"]
        db.add(existing)
        db.flush()
        return

    db.add(
        DrugInteraction(
            ingredient_a_id=ingredient_a_id,
            ingredient_b_id=ingredient_b_id,
            severity=payload["severity"],
            clinical_effect=payload["clinical_effect"],
            recommendation=payload["recommendation"],
            source_reference=payload["source_reference"],
        )
    )
    db.flush()


def seed_mvp_catalog(db: Session) -> dict[str, int]:
    dosage_forms = {item.code: item for item in (ensure_dosage_form(db, payload) for payload in DOSAGE_FORMS)}
    ingredients = {item.inn_name: item for item in (ensure_active_ingredient(db, payload) for payload in ACTIVE_INGREDIENTS)}
    presentation_ids: dict[str, str] = {}

    for payload in PRODUCTS:
        presentation = ensure_product(db, payload, dosage_forms, ingredients)
        presentation_ids[payload["key"]] = presentation.id

    for payload in EQUIVALENTS:
        ensure_equivalent(db, payload, presentation_ids)

    for payload in INTERACTIONS:
        ensure_interaction(db, payload, ingredients)

    db.commit()
    return {
        "countries": 2,
        "dosage_forms": len(DOSAGE_FORMS),
        "active_ingredients": len(ACTIVE_INGREDIENTS),
        "products": len(PRODUCTS),
        "equivalents": len(EQUIVALENTS),
        "interactions": len(INTERACTIONS),
    }


def main() -> None:
    with SessionLocal() as db:
        summary = seed_mvp_catalog(db)
    print(f"Seeded {DATASET_NAME}: {summary}")


if __name__ == "__main__":
    main()
