"""Ajouter les colonnes updated_at et est_actif à la table tresorerie_station

Revision ID: 5c9h6d0e8f1g
Revises: 4b8g5c9d7e0f
Create Date: 2025-12-14 20:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5c9h6d0e8f1g'
down_revision: Union[str, Sequence[str], None] = '4b8g5c9d7e0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les colonnes updated_at et est_actif à la table tresorerie_station si elles n'existent pas
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('tresorerie_station')]
    
    if 'updated_at' not in columns:
        op.add_column('tresorerie_station', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    if 'est_actif' not in columns:
        op.add_column('tresorerie_station', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Supprimer les colonnes updated_at et est_actif de la table tresorerie_station si elles existent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('tresorerie_station')]
    
    if 'est_actif' in columns:
        op.drop_column('tresorerie_station', 'est_actif')
    
    if 'updated_at' in columns:
        op.drop_column('tresorerie_station', 'updated_at')
