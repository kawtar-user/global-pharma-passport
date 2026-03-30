from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.services import billing as billing_service
from app.models.catalog import DrugEquivalent, DrugPresentation
from app.schemas.equivalents import (
    DrugEquivalentCreate,
    EquivalentPresentationSummary,
    EquivalentSearchNotice,
    EquivalentSearchResponse,
)


def create_equivalent(db: Session, payload: DrugEquivalentCreate) -> DrugEquivalent:
    if payload.source_drug_presentation_id == payload.target_drug_presentation_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source and target must be different")

    existing = db.scalar(
        select(DrugEquivalent).where(
            DrugEquivalent.source_drug_presentation_id == payload.source_drug_presentation_id,
            DrugEquivalent.target_drug_presentation_id == payload.target_drug_presentation_id,
            DrugEquivalent.equivalence_type == payload.equivalence_type,
        )
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Equivalent mapping already exists")

    source = db.get(DrugPresentation, payload.source_drug_presentation_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source presentation not found")
    target = db.get(DrugPresentation, payload.target_drug_presentation_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target presentation not found")

    item = DrugEquivalent(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_equivalent_mappings(db: Session) -> list[DrugEquivalent]:
    return list(db.scalars(select(DrugEquivalent).order_by(DrugEquivalent.updated_at.desc())))


def find_equivalents(
    db: Session,
    user: User,
    source_presentation_id: str,
    target_country_code: str | None = None,
) -> EquivalentSearchResponse:
    source = db.get(DrugPresentation, source_presentation_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source presentation not found")

    stmt = (
        select(DrugEquivalent)
        .options(
            joinedload(DrugEquivalent.source_presentation).joinedload(DrugPresentation.drug_product),
            joinedload(DrugEquivalent.target_presentation).joinedload(DrugPresentation.drug_product),
            joinedload(DrugEquivalent.target_presentation).joinedload(DrugPresentation.dosage_form),
        )
        .where(
            or_(
                DrugEquivalent.source_drug_presentation_id == source_presentation_id,
                DrugEquivalent.target_drug_presentation_id == source_presentation_id,
            )
        )
    )
    mappings = list(db.scalars(stmt))

    results: list[EquivalentPresentationSummary] = []
    seen_presentation_ids: set[str] = set()
    for mapping in mappings:
        target = (
            mapping.target_presentation
            if mapping.source_drug_presentation_id == source_presentation_id
            else mapping.source_presentation
        )
        if target_country_code and target.drug_product.country_code != target_country_code.upper():
            continue
        if target.id in seen_presentation_ids:
            continue
        seen_presentation_ids.add(target.id)
        results.append(
            EquivalentPresentationSummary(
                presentation_id=target.id,
                brand_name=target.drug_product.brand_name,
                country_code=target.drug_product.country_code,
                dosage_form=target.dosage_form.name,
                strength_text=target.strength_text,
                route=target.route,
            )
        )

    subscription = billing_service.get_current_subscription(db, user)
    limits = billing_service.get_plan_limits(subscription.plan_code)
    if limits.equivalent_results_per_search is not None:
        results = results[: limits.equivalent_results_per_search]

    notice = None
    if not results:
        target_label = target_country_code.upper() if target_country_code else "the selected country"
        notice = EquivalentSearchNotice(
            code="no_equivalent_found",
            message=f"No validated equivalent was found for this medication in {target_label}.",
        )

    return EquivalentSearchResponse(
        source_presentation_id=source_presentation_id,
        target_country_code=target_country_code.upper() if target_country_code else None,
        results=results,
        notice=notice,
    )
