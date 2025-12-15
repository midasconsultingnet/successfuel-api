"""Ajouter la colonne est_actif à la table utilisateur

Revision ID: 9f28eaa4b8a8
Revises: dea14a76789f
Create Date: 2025-12-14 18:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9f28eaa4b8a8'
down_revision: Union[str, Sequence[str], None] = 'dea14a76789f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter la colonne est_actif à la table utilisateur
    op.add_column('utilisateur', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Supprimer la colonne est_actif de la table utilisateur
    op.drop_column('utilisateur', 'est_actif')
