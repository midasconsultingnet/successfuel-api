"""Add description column to bilan_initial table

Revision ID: 004_add_description
Revises: 003_add_utilisateur_id
Create Date: 2025-12-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '004_add_description'
down_revision: Union[str, None] = '003_add_utilisateur_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add description column to bilan_initial table
    op.add_column('bilan_initial', sa.Column('description', sa.Text, nullable=True))


def downgrade() -> None:
    # Remove description column from bilan_initial table
    op.drop_column('bilan_initial', 'description')