from __future__ import annotations

from pathlib import Path

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260329_0001"
down_revision = None
branch_labels = None
depends_on = None


def _read_sql(filename: str) -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / "db" / "migrations" / filename).read_text(encoding="utf-8")


def upgrade() -> None:
    op.execute(_read_sql("001_init_global_pharma_passport.sql"))


def downgrade() -> None:
    op.execute(_read_sql("001_init_global_pharma_passport_down.sql"))
