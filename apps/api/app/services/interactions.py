from itertools import combinations

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalog import ActiveIngredient, DrugInteraction, DrugPresentation, DrugPresentationIngredient
from app.schemas.interactions import DrugInteractionCreate, InteractionCheckMatch, InteractionCheckResponse


def _ordered_pair(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def create_interaction(db: Session, payload: DrugInteractionCreate) -> DrugInteraction:
    if payload.ingredient_a_id == payload.ingredient_b_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredients must be distinct")

    ingredient_a_id, ingredient_b_id = _ordered_pair(payload.ingredient_a_id, payload.ingredient_b_id)
    known_ingredients = {
        item.id
        for item in db.scalars(
            select(ActiveIngredient).where(ActiveIngredient.id.in_([ingredient_a_id, ingredient_b_id]))
        )
    }
    if ingredient_a_id not in known_ingredients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="First active ingredient not found")
    if ingredient_b_id not in known_ingredients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Second active ingredient not found")

    existing = db.scalar(
        select(DrugInteraction).where(
            DrugInteraction.ingredient_a_id == ingredient_a_id,
            DrugInteraction.ingredient_b_id == ingredient_b_id,
        )
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Interaction already exists")

    item = DrugInteraction(
        ingredient_a_id=ingredient_a_id,
        ingredient_b_id=ingredient_b_id,
        severity=payload.severity,
        mechanism=payload.mechanism,
        clinical_effect=payload.clinical_effect,
        recommendation=payload.recommendation,
        source_reference=payload.source_reference,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_interactions(db: Session) -> list[DrugInteraction]:
    stmt = select(DrugInteraction).order_by(DrugInteraction.updated_at.desc())
    return list(db.scalars(stmt))


def check_interactions(db: Session, presentation_ids: list[str]) -> InteractionCheckResponse:
    normalized_presentation_ids = list(dict.fromkeys(presentation_ids))
    stmt = (
        select(DrugPresentation)
        .options(selectinload(DrugPresentation.ingredients))
        .where(DrugPresentation.id.in_(normalized_presentation_ids))
    )
    presentations = list(db.scalars(stmt))
    if len(presentations) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Add at least two different catalog medications to check interactions",
        )

    ingredient_ids = {
        ingredient.active_ingredient_id
        for presentation in presentations
        for ingredient in presentation.ingredients
    }
    if len(ingredient_ids) < 2:
        return InteractionCheckResponse(checked_pairs=0, matches=[])

    interaction_stmt = select(DrugInteraction).where(
        or_(
            DrugInteraction.ingredient_a_id.in_(ingredient_ids),
            DrugInteraction.ingredient_b_id.in_(ingredient_ids),
        )
    ).options(
        joinedload(DrugInteraction.ingredient_a),
        joinedload(DrugInteraction.ingredient_b),
    )
    interactions = list(db.scalars(interaction_stmt))
    indexed = {
        (item.ingredient_a_id, item.ingredient_b_id): item
        for item in interactions
    }

    presentation_ingredients = {
        presentation.id: {ingredient.active_ingredient_id for ingredient in presentation.ingredients}
        for presentation in presentations
    }

    matches: list[InteractionCheckMatch] = []
    checked_pairs = 0
    for presentation_a, presentation_b in combinations(presentations, 2):
        ingredient_pairs = {
            _ordered_pair(a, b)
            for a in presentation_ingredients[presentation_a.id]
            for b in presentation_ingredients[presentation_b.id]
            if a != b
        }
        checked_pairs += len(ingredient_pairs)
        for pair in ingredient_pairs:
            interaction = indexed.get(pair)
            if interaction:
                matches.append(
                    InteractionCheckMatch(
                        interaction_id=interaction.id,
                        ingredient_a_id=interaction.ingredient_a_id,
                        ingredient_b_id=interaction.ingredient_b_id,
                        ingredient_a_name=interaction.ingredient_a.inn_name,
                        ingredient_b_name=interaction.ingredient_b.inn_name,
                        severity=interaction.severity,
                        clinical_effect=interaction.clinical_effect,
                        recommendation=interaction.recommendation,
                    )
                )

    return InteractionCheckResponse(checked_pairs=checked_pairs, matches=matches)
