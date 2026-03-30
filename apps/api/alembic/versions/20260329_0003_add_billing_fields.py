from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "20260329_0003"
down_revision = "20260329_0002"
branch_labels = None
depends_on = None


def _read_sql(filename: str) -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / "db" / "migrations" / filename).read_text(encoding="utf-8")


def upgrade() -> None:
    op.execute(_read_sql("003_add_billing_fields.sql"))


def downgrade() -> None:
    op.execute(_read_sql("003_add_billing_fields_down.sql"))
