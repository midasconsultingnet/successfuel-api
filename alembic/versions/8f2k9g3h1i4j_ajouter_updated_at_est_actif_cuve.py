"""Ajouter les colonnes updated_at et est_actif à la table cuve

Revision ID: 8f2k9g3h1i4j
Revises: 7e1j8f2g0h3i
Create Date: 2025-12-14 21:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8f2k9g3h1i4j'
down_revision: Union[str, Sequence[str], None] = '7e1j8f2g0h3i'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les colonnes updated_at et est_actif à la table cuve si elles n'existent pas
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('cuve')]
    
    if 'updated_at' not in columns:
        op.add_column('cuve', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    if 'est_actif' not in columns:
        op.add_column('cuve', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Supprimer les colonnes updated_at et est_actif de la table cuve si elles existent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('cuve')]
    
    if 'est_actif' in columns:
        op.drop_column('cuve', 'est_actif')
    
    if 'updated_at' in columns:
        op.drop_column('cuve', 'updated_at')
