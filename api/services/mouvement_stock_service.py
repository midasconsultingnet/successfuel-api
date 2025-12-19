from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import datetime, timezone
from ..models.mouvement_stock import MouvementStock
from ..models.stock import StockProduit
from ..models.produit import Produit
from .cout_moyen_service import mettre_a_jour_cout_moyen_produit


def enregistrer_mouvement_stock(
    db: Session,
    produit_id: str,
    station_id: str,
    type_mouvement: str,
    quantite: float,
    cout_unitaire: Optional[float] = None,
    utilisateur_id: Optional[str] = None,
    module_origine: str = "inconnu",
    reference_origine: str = "inconnu",
    date_mouvement: Optional[datetime] = None
):
    """
    Enregistre un mouvement de stock et met à jour le stock théorique et le coût moyen du produit
    """
    if date_mouvement is None:
        date_mouvement = datetime.now(timezone.utc)

    # Créer le mouvement de stock
    mouvement = MouvementStock(
        produit_id=produit_id,
        station_id=station_id,
        type_mouvement=type_mouvement,
        quantite=quantite,
        cout_unitaire=cout_unitaire,
        date_mouvement=date_mouvement,
        utilisateur_id=utilisateur_id,
        module_origine=module_origine,
        reference_origine=reference_origine
    )

    db.add(mouvement)
    
    # Mettre à jour la quantité théorique dans le stock
    mettre_a_jour_stock_theorique(db, produit_id, station_id, type_mouvement, quantite)

    db.commit()
    db.refresh(mouvement)

    # Mettre à jour le coût moyen du produit
    mettre_a_jour_cout_moyen_produit(db, produit_id, station_id)

    return mouvement


def mettre_a_jour_stock_theorique(
    db: Session,
    produit_id: str,
    station_id: str,
    type_mouvement: str,
    quantite: float
):
    """
    Met à jour la quantité théorique de stock pour un produit et une station donnés
    """
    # Récupérer ou créer l'enregistrement de stock
    stock = db.query(StockProduit).filter(
        and_(
            StockProduit.produit_id == produit_id,
            StockProduit.station_id == station_id
        )
    ).first()

    if stock is None:
        # Créer un nouvel enregistrement de stock s'il n'existe pas
        stock = StockProduit(
            produit_id=produit_id,
            station_id=station_id,
            quantite_theorique=0,
            quantite_reelle=0
        )
        db.add(stock)

    # Mettre à jour la quantité théorique selon le type de mouvement
    if type_mouvement in ['entree', 'stock_initial', 'ajustement_positif', 'inventaire_positif']:
        stock.quantite_theorique += quantite
    elif type_mouvement in ['sortie', 'ajustement_negatif', 'inventaire_negatif']:
        stock.quantite_theorique -= quantite
    else:
        # Pour d'autres types de mouvements, ignorer ou lever une exception selon les besoins
        pass

    # S'assurer que la quantité ne soit pas négative
    if stock.quantite_theorique < 0:
        stock.quantite_theorique = 0

    db.commit()