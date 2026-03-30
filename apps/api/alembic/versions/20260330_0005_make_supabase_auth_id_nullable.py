from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "20260330_0005"
down_revision = "20260329_0004"
branch_labels = None
depends_on = None


def _read_sql(filename: str) -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / "db" / "migrations" / filename).read_text(encoding="utf-8")


def upgrade() -> None:
    op.execute(_read_sql("005_make_supabase_auth_id_nullable.sql"))


def downgrade() -> None:
    op.execute(_read_sql("005_make_supabase_auth_id_nullable_down.sql"))
