from __future__ import annotations

from sqlalchemy import func, or_, select

from app.core.database import SessionLocal
from app.models.catalog import DrugProduct
from app.seeds.load_mvp_catalog import seed_mvp_catalog
from app.seeds.mvp_maroc_france import PRODUCTS


def _mvp_product_conditions():
    return [
        (
            DrugProduct.brand_name == payload["brand_name"],
            DrugProduct.country_code == payload["country_code"],
        )
        for payload in PRODUCTS
    ]


def main() -> None:
    with SessionLocal() as db:
        expected_pairs = _mvp_product_conditions()
        existing_mvp_products = db.scalar(
            select(func.count(DrugProduct.id)).where(
                or_(*[pair[0] & pair[1] for pair in expected_pairs])
            )
        ) or 0
        total_products_before = db.scalar(select(func.count(DrugProduct.id))) or 0

        if existing_mvp_products < len(PRODUCTS):
            summary = seed_mvp_catalog(db)
            total_products_after = db.scalar(select(func.count(DrugProduct.id))) or 0
            print(
                "[startup] Catalog seed completed:"
                f" before={total_products_before} after={total_products_after} summary={summary}"
            )
            return

        print(
            "[startup] Catalog seed skipped:"
            f" total_products={total_products_before} mvp_products={existing_mvp_products}"
        )


if __name__ == "__main__":
    main()
