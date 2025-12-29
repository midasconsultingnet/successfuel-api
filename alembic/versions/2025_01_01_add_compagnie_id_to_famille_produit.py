"""add compagnie_id to famille_produit

Revision ID: 123456789012
Revises: 000000000000
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '123456789012'
down_revision = '000000000000'  # You should update this to the latest revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Add compagnie_id column as nullable first
    op.add_column('famille_produit', sa.Column('compagnie_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Update existing records - this is a simplified approach
    # In a real scenario, you would need to assign existing families to appropriate companies
    # For now, we'll skip this step and make the column required for new records only
    # The application logic will ensure new families have the correct company_id

    # Create foreign key constraint
    op.create_foreign_key('famille_produit_compagnie_id_fkey', 'famille_produit', 'compagnie', ['compagnie_id'], ['id'])

    # Make the column non-nullable after populating with appropriate values
    # Since we can't automatically assign existing families to companies without business logic,
    # we'll keep it nullable for now and let the application handle it
    # op.alter_column('famille_produit', 'compagnie_id', nullable=False)


def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('famille_produit_compagnie_id_fkey', 'famille_produit', type_='foreignkey')

    # Drop the column
    op.drop_column('famille_produit', 'compagnie_id')