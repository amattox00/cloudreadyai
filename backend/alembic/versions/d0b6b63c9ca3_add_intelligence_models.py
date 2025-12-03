"""add intelligence models

Revision ID: d0b6b63c9ca3
Revises: auth_schema
Create Date: 2025-11-22 23:59:35.837516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0b6b63c9ca3'
down_revision: Union[str, Sequence[str], None] = 'auth_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
