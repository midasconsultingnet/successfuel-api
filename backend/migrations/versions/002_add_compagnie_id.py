"""Add compagnie_id column to plan_comptable table

Revision ID: 002_add_compagnie_id
Revises: 001_add_temperature_to_cuves
Create Date: 2025-12-01 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '002_add_compagnie_id'
down_revision: Union[str, None] = '001_add_temperature_to_cuves'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add compagnie_id column to plan_comptable table
    op.add_column('plan_comptable', sa.Column('compagnie_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create index for the new column
    op.create_index(op.f('ix_plan_comptable_compagnie_id'), 'plan_comptable', ['compagnie_id'])
    
    # Add foreign key constraint referencing compagnies table
    op.create_foreign_key('fk_plan_comptable_compagnie_id', 'plan_comptable', 'compagnies', 
                          ['compagnie_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_plan_comptable_compagnie_id', 'plan_comptable', type_='foreignkey')
    
    # Drop index
    op.drop_index(op.f('ix_plan_comptable_compagnie_id'), table_name='plan_comptable')
    
    # Remove compagnie_id column from plan_comptable table
    op.drop_column('plan_comptable', 'compagnie_id')