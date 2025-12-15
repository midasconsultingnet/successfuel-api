"""Ajouter les colonnes communes manquantes aux tables existantes

Revision ID: dea14a76789f
Revises: 
Create Date: 2025-12-14 16:43:14.124116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dea14a76789f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def execute_ignore_duplicate_column_error(sql):
    """
    Fonction pour exécuter une commande SQL en ignorant les erreurs de colonne dupliquée
    """
    from sqlalchemy import text
    from alembic import context
    from sqlalchemy.exc import ProgrammingError
    
    # Obtenir la connexion
    conn = context.get_context().bind
    
    try:
        conn.execute(text(sql))
    except ProgrammingError as e:
        if 'already exists' in str(e):
            print(f"Colonne déjà existante, ignorée: {sql}")
        else:
            raise


def upgrade() -> None:
    # Ajouter les colonnes aux tables existantes qui devraient hériter de BaseModel
    # En ignorant les erreurs si elles existent déjà
    
    # Pour la table utilisateur
    try:
        op.add_column('utilisateur', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('utilisateur', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('utilisateur', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table compagnie
    try:
        op.add_column('compagnie', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('compagnie', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('compagnie', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table tiers
    try:
        op.add_column('tiers', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('tiers', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('tiers', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table produit
    try:
        op.add_column('produit', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('produit', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('produit', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table station
    try:
        op.add_column('station', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('station', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('station', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table methode_paiement
    try:
        op.add_column('methode_paiement', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('methode_paiement', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('methode_paiement', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table carburant
    try:
        op.add_column('carburant', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('carburant', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('carburant', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table affectation_utilisateur_station
    try:
        op.add_column('affectation_utilisateur_station', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('affectation_utilisateur_station', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('affectation_utilisateur_station', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table profils
    try:
        op.add_column('profils', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('profils', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('profils', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table profil_module
    try:
        op.add_column('profil_module', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('profil_module', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('profil_module', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    # Pour la table utilisateur_profil
    try:
        op.add_column('utilisateur_profil', sa.Column('est_actif', sa.Boolean(), server_default='true', nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('utilisateur_profil', sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante
    
    try:
        op.add_column('utilisateur_profil', sa.Column('date_modification', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    except:
        pass  # Colonne déjà existante


def downgrade() -> None:
    # Supprimer les colonnes ajoutées
    op.drop_column('utilisateur', 'date_modification')
    op.drop_column('utilisateur', 'date_creation')
    op.drop_column('utilisateur', 'est_actif')
    
    op.drop_column('compagnie', 'date_modification')
    op.drop_column('compagnie', 'date_creation')
    op.drop_column('compagnie', 'est_actif')
    
    op.drop_column('tiers', 'date_modification')
    op.drop_column('tiers', 'date_creation')
    op.drop_column('tiers', 'est_actif')
    
    op.drop_column('produit', 'date_modification')
    op.drop_column('produit', 'date_creation')
    op.drop_column('produit', 'est_actif')
    
    op.drop_column('station', 'date_modification')
    op.drop_column('station', 'date_creation')
    op.drop_column('station', 'est_actif')
    
    op.drop_column('methode_paiement', 'date_modification')
    op.drop_column('methode_paiement', 'date_creation')
    op.drop_column('methode_paiement', 'est_actif')
    
    op.drop_column('carburant', 'date_modification')
    op.drop_column('carburant', 'date_creation')
    op.drop_column('carburant', 'est_actif')
    
    op.drop_column('affectation_utilisateur_station', 'date_modification')
    op.drop_column('affectation_utilisateur_station', 'date_creation')
    op.drop_column('affectation_utilisateur_station', 'est_actif')
    
    op.drop_column('profils', 'date_modification')
    op.drop_column('profils', 'date_creation')
    op.drop_column('profils', 'est_actif')
    
    op.drop_column('profil_module', 'date_modification')
    op.drop_column('profil_module', 'date_creation')
    op.drop_column('profil_module', 'est_actif')
    
    op.drop_column('utilisateur_profil', 'date_modification')
    op.drop_column('utilisateur_profil', 'date_creation')
    op.drop_column('utilisateur_profil', 'est_actif')
