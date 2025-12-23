"""Ajouter des indexes critiques pour les performances

Revision ID: a1b2c3d4e5f6
Revises: dea14a76789f
Create Date: 2025-12-16 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'dea14a76789f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Indexes sur les clés étrangères fréquemment utilisées
    op.create_index('idx_achats_station_id', 'achats', ['station_id'])
    op.create_index('idx_achats_compagnie_id', 'achats', ['compagnie_id'])
    op.create_index('idx_achats_fournisseur_id', 'achats', ['fournisseur_id'])
    
    op.create_index('idx_achats_details_achat_id', 'achats_details', ['achat_id'])
    op.create_index('idx_achats_details_produit_id', 'achats_details', ['produit_id'])
    
    op.create_index('idx_ventes_station_id', 'ventes', ['station_id'])
    op.create_index('idx_ventes_compagnie_id', 'ventes', ['compagnie_id'])
    op.create_index('idx_ventes_client_id', 'ventes', ['client_id'])
    op.create_index('idx_ventes_trésorerie_station_id', 'ventes', ['trésorerie_station_id'])
    
    op.create_index('idx_ventes_details_vente_id', 'ventes_details', ['vente_id'])
    op.create_index('idx_ventes_details_produit_id', 'ventes_details', ['produit_id'])
    
    op.create_index('idx_stock_produit_produit_id', 'stock_produit', ['produit_id'])
    op.create_index('idx_stock_produit_station_id', 'stock_produit', ['station_id'])
    
    op.create_index('idx_tresorerie_station_station_id', 'tresorerie_station', ['station_id'])
    op.create_index('idx_tresorerie_station_tresorerie_id', 'tresorerie_station', ['tresorerie_id'])
    
    op.create_index('idx_mouvement_tresorerie_station_id', 'mouvement_tresorerie', ['trésorerie_station_id'])
    op.create_index('idx_mouvement_tresorerie_date', 'mouvement_tresorerie', ['date_mouvement'])
    
    op.create_index('idx_mouvement_stock_cuve_cuve_id', 'mouvement_stock_cuve', ['cuve_id'])
    op.create_index('idx_mouvement_stock_cuve_date', 'mouvement_stock_cuve', ['date_mouvement'])
    op.create_index('idx_mouvement_stock_cuve_type', 'mouvement_stock_cuve', ['type_mouvement'])
    
    op.create_index('idx_vente_carburant_station_id', 'vente_carburant', ['station_id'])
    op.create_index('idx_vente_carburant_cuve_id', 'vente_carburant', ['cuve_id'])
    op.create_index('idx_vente_carburant_date', 'vente_carburant', ['date_vente'])
    
    op.create_index('idx_tiers_compagnie_id', 'tiers', ['compagnie_id'])
    op.create_index('idx_tiers_type', 'tiers', ['type'])
    
    op.create_index('idx_station_compagnie_id', 'station', ['compagnie_id'])
    
    op.create_index('idx_utilisateur_compagnie_id', 'utilisateur', ['compagnie_id'])
    
    op.create_index('idx_avoirs_tiers_id', 'avoirs', ['tiers_id'])
    op.create_index('idx_avoirs_compagnie_id', 'avoirs', ['compagnie_id'])
    
    op.create_index('idx_lot_produit_id', 'lot', ['produit_id'])
    op.create_index('idx_lot_station_id', 'lot', ['station_id'])
    
    op.create_index('idx_inventaire_station_id', 'inventaires', ['station_id'])
    op.create_index('idx_inventaire_compagnie_id', 'inventaires', ['compagnie_id'])
    op.create_index('idx_inventaire_date', 'inventaires', ['date_inventaire'])
    
    op.create_index('idx_ecart_inventaire_inventaire_id', 'ecart_inventaire', ['inventaire_id'])
    op.create_index('idx_ecart_inventaire_produit_id', 'ecart_inventaire', ['produit_id'])
    
    # Indexes sur les colonnes de statut et de date fréquemment filtrées
    op.create_index('idx_achats_statut', 'achats', ['statut'])
    op.create_index('idx_ventes_statut', 'ventes', ['statut'])
    op.create_index('idx_inventaire_statut', 'inventaires', ['statut'])
    
    # Indexes sur les dates pour les requêtes de plage
    op.create_index('idx_achats_date', 'achats', ['date'])
    op.create_index('idx_ventes_date', 'ventes', ['date'])


def downgrade() -> None:
    # Suppression des indexes dans l'ordre inverse
    op.drop_index('idx_ventes_date', table_name='ventes')
    op.drop_index('idx_achats_date', table_name='achats')
    
    op.drop_index('idx_inventaire_statut', table_name='inventaires')
    op.drop_index('idx_ventes_statut', table_name='ventes')
    op.drop_index('idx_achats_statut', table_name='achats')
    
    op.drop_index('idx_ecart_inventaire_produit_id', table_name='ecart_inventaire')
    op.drop_index('idx_ecart_inventaire_inventaire_id', table_name='ecart_inventaire')
    
    op.drop_index('idx_inventaire_date', table_name='inventaires')
    op.drop_index('idx_inventaire_compagnie_id', table_name='inventaires')
    op.drop_index('idx_inventaire_station_id', table_name='inventaires')
    
    op.drop_index('idx_lot_station_id', table_name='lot')
    op.drop_index('idx_lot_produit_id', table_name='lot')
    
    op.drop_index('idx_avoirs_compagnie_id', table_name='avoirs')
    op.drop_index('idx_avoirs_tiers_id', table_name='avoirs')
    
    op.drop_index('idx_utilisateur_compagnie_id', table_name='utilisateur')
    
    op.drop_index('idx_station_compagnie_id', table_name='station')
    
    op.drop_index('idx_tiers_type', table_name='tiers')
    op.drop_index('idx_tiers_compagnie_id', table_name='tiers')
    
    op.drop_index('idx_vente_carburant_date', table_name='vente_carburant')
    op.drop_index('idx_vente_carburant_cuve_id', table_name='vente_carburant')
    op.drop_index('idx_vente_carburant_station_id', table_name='vente_carburant')
    
    op.drop_index('idx_mouvement_stock_cuve_type', table_name='mouvement_stock_cuve')
    op.drop_index('idx_mouvement_stock_cuve_date', table_name='mouvement_stock_cuve')
    op.drop_index('idx_mouvement_stock_cuve_cuve_id', table_name='mouvement_stock_cuve')
    
    op.drop_index('idx_mouvement_tresorerie_date', table_name='mouvement_tresorerie')
    op.drop_index('idx_mouvement_tresorerie_station_id', table_name='mouvement_tresorerie')
    
    op.drop_index('idx_tresorerie_station_tresorerie_id', table_name='tresorerie_station')
    op.drop_index('idx_tresorerie_station_station_id', table_name='tresorerie_station')
    
    op.drop_index('idx_stock_produit_station_id', table_name='stock_produit')
    op.drop_index('idx_stock_produit_produit_id', table_name='stock_produit')
    
    op.drop_index('idx_ventes_details_produit_id', table_name='ventes_details')
    op.drop_index('idx_ventes_details_vente_id', table_name='ventes_details')
    
    op.drop_index('idx_ventes_trésorerie_station_id', table_name='ventes')
    op.drop_index('idx_ventes_client_id', table_name='ventes')
    op.drop_index('idx_ventes_compagnie_id', table_name='ventes')
    op.drop_index('idx_ventes_station_id', table_name='ventes')
    
    op.drop_index('idx_achats_details_produit_id', table_name='achats_details')
    op.drop_index('idx_achats_details_achat_id', table_name='achats_details')
    
    op.drop_index('idx_achats_fournisseur_id', table_name='achats')
    op.drop_index('idx_achats_compagnie_id', table_name='achats')
    op.drop_index('idx_achats_station_id', table_name='achats')