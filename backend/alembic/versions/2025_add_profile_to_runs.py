"""Add profile column to analysis_run table (safe / idempotent)"""

from alembic import op
import sqlalchemy as sa  # noqa: F401


revision = "2025_add_profile_to_runs"
# We still keep it hanging off d426ff6be5d9
down_revision = "d426ff6be5d9"
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL with IF EXISTS / IF NOT EXISTS to avoid errors
    op.execute(
        """
        ALTER TABLE IF EXISTS analysis_run
        ADD COLUMN IF NOT EXISTS profile VARCHAR;
        """
    )


def downgrade():
    # Make downgrade also safe / no-op if things are missing
    op.execute(
        """
        ALTER TABLE IF EXISTS analysis_run
        DROP COLUMN IF EXISTS profile;
        """
    )
