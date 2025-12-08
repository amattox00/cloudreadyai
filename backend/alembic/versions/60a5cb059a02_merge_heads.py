"""Merge heads 2025_add_profile_to_runs and d0b6b63c9ca3"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

revision = "60a5cb059a02_merge_heads"
# ✅ Merge the two *actual* heads: intelligence branch + profile branch
down_revision = ("d0b6b63c9ca3", "2025_add_profile_to_runs")
branch_labels = None
depends_on = None


def upgrade():
    # No schema changes; this just merges the two heads.
    pass


def downgrade():
    # No-op downgrade as well.
    pass
