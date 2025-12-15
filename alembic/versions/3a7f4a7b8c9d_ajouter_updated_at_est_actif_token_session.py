"""Ajouter les colonnes updated_at et est_actif à la table token_session

Revision ID: 3a7f4a7b8c9d
Revises: 9f28eaa4b8a8
Create Date: 2025-12-14 19:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3a7f4a7b8c9d'
down_revision: Union[str, Sequence[str], None] = '9f28eaa4b8a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les colonnes updated_at et est_actif à la table token_session si elles n'existent pas
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('token_session')]

    if 'updated_at' not in columns:
        op.add_column('token_session', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    if 'est_actif' not in columns:
        op.add_column('token_session', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Supprimer la colonne est_actif de la table token_session si elle existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('token_session')]

    if 'est_actif' in columns:
        op.drop_column('token_session', 'est_actif')

    if 'updated_at' in columns:
        op.drop_column('token_session', 'updated_at')
