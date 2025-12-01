"""Add temperature column to cuves table

Revision ID: 001_add_temperature_to_cuves
Revises: 
Create Date: 2025-11-27 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_add_temperature_to_cuves'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add temperature column to cuves table
    op.add_column('cuves', sa.Column('temperature', sa.Numeric(5, 2), server_default='0', nullable=False))


def downgrade() -> None:
    # Remove temperature column from cuves table
    op.drop_column('cuves', 'temperature')