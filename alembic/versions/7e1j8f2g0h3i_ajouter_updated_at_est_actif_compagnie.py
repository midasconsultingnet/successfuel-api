"""Ajouter les colonnes updated_at et est_actif à la table compagnie

Revision ID: 7e1j8f2g0h3i
Revises: 6d0i7e1f9g2h
Create Date: 2025-12-14 21:15:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7e1j8f2g0h3i'
down_revision: Union[str, Sequence[str], None] = '6d0i7e1f9g2h'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les colonnes updated_at et est_actif à la table compagnie si elles n'existent pas
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('compagnie')]
    
    if 'updated_at' not in columns:
        op.add_column('compagnie', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    if 'est_actif' not in columns:
        op.add_column('compagnie', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Supprimer les colonnes updated_at et est_actif de la table compagnie si elles existent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('compagnie')]
    
    if 'est_actif' in columns:
        op.drop_column('compagnie', 'est_actif')
    
    if 'updated_at' in columns:
        op.drop_column('compagnie', 'updated_at')
