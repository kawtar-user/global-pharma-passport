from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "20260331_0006"
down_revision = "20260330_0005"
branch_labels = None
depends_on = None


def _read_sql(filename: str) -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / "db" / "migrations" / filename).read_text(encoding="utf-8")


def upgrade() -> None:
    op.execute(_read_sql("006_add_email_verification_tokens.sql"))


def downgrade() -> None:
    op.execute(_read_sql("006_add_email_verification_tokens_down.sql"))
