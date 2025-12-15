"""Ajouter la colonne seuil_stock_min à la table produit

Revision ID: abc123def456
Revises: dea14a76789f
Create Date: 2025-12-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = 'dea14a76789f'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne seuil_stock_min à la table produit
    op.add_column('produit', sa.Column('seuil_stock_min', sa.Float, server_default='0', nullable=False))
    op.add_column('produit', sa.Column('cout_moyen', sa.Float, server_default='0', nullable=False))


def downgrade():
    # Supprimer les colonnes ajoutées
    op.drop_column('produit', 'seuil_stock_min')
    op.drop_column('produit', 'cout_moyen')