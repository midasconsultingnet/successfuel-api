"""Add utilisateur_id column to bilan_initial table

Revision ID: 003_add_utilisateur_id
Revises: 002_add_compagnie_id
Create Date: 2025-12-01 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '003_add_utilisateur_id'
down_revision: Union[str, None] = '002_add_compagnie_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add utilisateur_id column to bilan_initial table
    op.add_column('bilan_initial', sa.Column('utilisateur_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create index for the new column
    op.create_index(op.f('ix_bilan_initial_utilisateur_id'), 'bilan_initial', ['utilisateur_id'])
    
    # Add foreign key constraint referencing utilisateurs table
    op.create_foreign_key('fk_bilan_initial_utilisateur_id', 'bilan_initial', 'utilisateurs', 
                          ['utilisateur_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_bilan_initial_utilisateur_id', 'bilan_initial', type_='foreignkey')
    
    # Drop index
    op.drop_index(op.f('ix_bilan_initial_utilisateur_id'), table_name='bilan_initial')
    
    # Remove utilisateur_id column from bilan_initial table
    op.drop_column('bilan_initial', 'utilisateur_id')