from __future__ import annotations

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.catalog import DrugProduct
from app.seeds.load_mvp_catalog import seed_mvp_catalog


def main() -> None:
    with SessionLocal() as db:
        existing_products = db.scalar(select(func.count(DrugProduct.id))) or 0
        if existing_products > 0:
            print(f"[startup] Catalog seed skipped: {existing_products} products already present.")
            return

        summary = seed_mvp_catalog(db)
        print(f"[startup] Catalog seed completed: {summary}")


if __name__ == "__main__":
    main()
