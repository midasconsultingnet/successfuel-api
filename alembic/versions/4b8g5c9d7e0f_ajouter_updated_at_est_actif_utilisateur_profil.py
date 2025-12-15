"""Ajouter les colonnes updated_at et est_actif à la table utilisateur_profil

Revision ID: 4b8g5c9d7e0f
Revises: 3a7f4a7b8c9d
Create Date: 2025-12-14 20:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4b8g5c9d7e0f'
down_revision: Union[str, Sequence[str], None] = '3a7f4a7b8c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les colonnes updated_at et est_actif à la table utilisateur_profil si elles n'existent pas
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('utilisateur_profil')]
    
    if 'updated_at' not in columns:
        op.add_column('utilisateur_profil', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    if 'est_actif' not in columns:
        op.add_column('utilisateur_profil', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Supprimer les colonnes updated_at et est_actif de la table utilisateur_profil si elles existent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('utilisateur_profil')]
    
    if 'est_actif' in columns:
        op.drop_column('utilisateur_profil', 'est_actif')
    
    if 'updated_at' in columns:
        op.drop_column('utilisateur_profil', 'updated_at')
