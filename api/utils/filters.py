from typing import Optional
from pydantic import Field, BaseModel
from fastapi import Query
from .pagination import BaseFilterParams


class ProduitFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les produits
    """
    nom: Optional[str] = Query(None, description="Filtrer par nom de produit")
    code: Optional[str] = Query(None, description="Filtrer par code de produit")
    famille_id: Optional[str] = Query(None, description="Filtrer par famille de produit")
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    type_produit: Optional[str] = Query(None, description="Filtrer par type de produit")


class StockFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les stocks
    """
    produit_id: Optional[str] = Query(None, description="Filtrer par produit")
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    quantite_min: Optional[float] = Query(None, ge=0, description="Quantité minimale en stock")
    quantite_max: Optional[float] = Query(None, ge=0, description="Quantité maximale en stock")


class TiersFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les tiers
    """
    nom: Optional[str] = Query(None, description="Filtrer par nom du tiers")
    type: Optional[str] = Query(None, description="Filtrer par type de tiers")
    code: Optional[str] = Query(None, description="Filtrer par code du tiers")
    email: Optional[str] = Query(None, description="Filtrer par email du tiers")
    telephone: Optional[str] = Query(None, description="Filtrer par téléphone du tiers")


class AchatFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les achats
    """
    fournisseur_id: Optional[str] = Query(None, description="Filtrer par fournisseur")
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (format: YYYY-MM-DD)")
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (format: YYYY-MM-DD)")
    numero_bl: Optional[str] = Query(None, description="Filtrer par numéro de bon de livraison")
    numero_facture: Optional[str] = Query(None, description="Filtrer par numéro de facture")


class VenteFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les ventes
    """
    client_id: Optional[str] = Query(None, description="Filtrer par client")
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (format: YYYY-MM-DD)")
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (format: YYYY-MM-DD)")
    type_vente: Optional[str] = Query(None, description="Filtrer par type de vente")
    statut: Optional[str] = Query(None, description="Filtrer par statut de la vente")


class LivraisonFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les livraisons
    """
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    cuve_id: Optional[str] = Query(None, description="Filtrer par cuve")
    carburant_id: Optional[str] = Query(None, description="Filtrer par carburant")
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (format: YYYY-MM-DD)")
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (format: YYYY-MM-DD)")
    fournisseur_id: Optional[str] = Query(None, description="Filtrer par fournisseur")


class TresorerieFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les tresoreries
    """
    nom: Optional[str] = Query(None, description="Filtrer par nom de trésorerie")
    type: Optional[str] = Query(None, description="Filtrer par type de trésorerie")
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    solde_min: Optional[float] = Query(None, ge=0, description="Solde minimum")
    solde_max: Optional[float] = Query(None, ge=0, description="Solde maximum")


class SalaireFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les salaires
    """
    employe_id: Optional[str] = Query(None, description="Filtrer par employé")
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (format: YYYY-MM-DD)")
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (format: YYYY-MM-DD)")
    montant_min: Optional[float] = Query(None, ge=0, description="Montant minimum")
    montant_max: Optional[float] = Query(None, ge=0, description="Montant maximum")


class ImmobilisationFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les immobilisations
    """
    nom: Optional[str] = Query(None, description="Filtrer par nom d'immobilisation")
    code: Optional[str] = Query(None, description="Filtrer par code d'immobilisation")
    type: Optional[str] = Query(None, description="Filtrer par type d'immobilisation")
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    valeur_min: Optional[float] = Query(None, ge=0, description="Valeur minimum")
    valeur_max: Optional[float] = Query(None, ge=0, description="Valeur maximum")


class ChargeFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les charges
    """
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie de charge")
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (format: YYYY-MM-DD)")
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (format: YYYY-MM-DD)")
    montant_min: Optional[float] = Query(None, ge=0, description="Montant minimum")
    montant_max: Optional[float] = Query(None, ge=0, description="Montant maximum")
    station_id: Optional[str] = Query(None, description="Filtrer par station")


class FamilleProduitFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les familles de produits
    """
    nom: Optional[str] = Query(None, description="Filtrer par nom de famille")
    code: Optional[str] = Query(None, description="Filtrer par code de famille")


class VenteCarburantFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les ventes de carburant
    """
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    cuve_id: Optional[str] = Query(None, description="Filtrer par cuve")
    pistolet_id: Optional[str] = Query(None, description="Filtrer par pistolet")
    pompiste: Optional[str] = Query(None, description="Filtrer par pompiste")
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (format: YYYY-MM-DD)")
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (format: YYYY-MM-DD)")
    quantite_min: Optional[float] = Query(None, ge=0, description="Quantité minimum vendue")
    quantite_max: Optional[float] = Query(None, ge=0, description="Quantité maximum vendue")


class MouvementStockFilterParams(BaseFilterParams):
    """
    Paramètres de filtre pour les mouvements de stock
    """
    station_id: Optional[str] = Query(None, description="Filtrer par station")
    type_mouvement: Optional[str] = Query(None, description="Filtrer par type de mouvement (entree, sortie, ajustement, etc.)")
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (format: YYYY-MM-DD)")
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (format: YYYY-MM-DD)")
    module_origine: Optional[str] = Query(None, description="Filtrer par module d'origine du mouvement")
    utilisateur_id: Optional[str] = Query(None, description="Filtrer par utilisateur qui a effectué le mouvement")