"""Ajouter les colonnes updated_at et est_actif à la table station

Revision ID: 6d0i7e1f9g2h
Revises: 5c9h6d0e8f1g
Create Date: 2025-12-14 21:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6d0i7e1f9g2h'
down_revision: Union[str, Sequence[str], None] = '5c9h6d0e8f1g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les colonnes updated_at et est_actif à la table station si elles n'existent pas
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('station')]
    
    if 'updated_at' not in columns:
        op.add_column('station', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    if 'est_actif' not in columns:
        op.add_column('station', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Supprimer les colonnes updated_at et est_actif de la table station si elles existent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('station')]
    
    if 'est_actif' in columns:
        op.drop_column('station', 'est_actif')
    
    if 'updated_at' in columns:
        op.drop_column('station', 'updated_at')
