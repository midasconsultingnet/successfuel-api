"""Add fields for three-stage process

Revision ID: 202601071200
Revises: 
Create Date: 2026-01-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '202601071200'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to achat_carburant table
    op.add_column('achat_carburant', sa.Column('date_validation', sa.DateTime(timezone=True), nullable=True))
    op.add_column('achat_carburant', sa.Column('date_livraison', sa.DateTime(timezone=True), nullable=True))
    op.add_column('achat_carburant', sa.Column('montant_reel', sa.Numeric(15, 2), nullable=True))
    op.add_column('achat_carburant', sa.Column('ecart_achat_livraison', sa.Numeric(15, 2), nullable=True))
    
    # Update the statut column values: change "facturé" to "livré"
    op.execute("UPDATE achat_carburant SET statut = 'livré' WHERE statut = 'facturé'")


def downgrade():
    # Remove new columns from achat_carburant table
    op.drop_column('achat_carburant', 'ecart_achat_livraison')
    op.drop_column('achat_carburant', 'montant_reel')
    op.drop_column('achat_carburant', 'date_livraison')
    op.drop_column('achat_carburant', 'date_validation')
    
    # Revert the statut column values: change "livré" back to "facturé"
    op.execute("UPDATE achat_carburant SET statut = 'facturé' WHERE statut = 'livré'")