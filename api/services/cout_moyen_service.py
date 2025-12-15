from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from ..models.produit import Produit
from ..models.mouvement_stock import MouvementStock
from decimal import Decimal


def calculer_cout_moyen_pondere(db: Session, produit_id: str, station_id: str) -> float:
    """
    Calcule le coût moyen pondéré d'un produit pour une station spécifique
    selon la formule : (Qté en stock * Coût moyen précédent + Qté nouvellement entrée * Coût unitaire) / (Qté en stock + Qté nouvellement entrée)
    
    :param db: Session SQLAlchemy
    :param produit_id: ID du produit
    :param station_id: ID de la station
    :return: Coût moyen pondéré calculé
    """
    
    # Récupérer les mouvements de stock pour ce produit et cette station
    mouvements = db.query(MouvementStock).filter(
        and_(
            MouvementStock.produit_id == produit_id,
            MouvementStock.station_id == station_id
        )
    ).order_by(MouvementStock.date_mouvement).all()

    if not mouvements:
        # Si aucun mouvement, le coût moyen est 0
        return 0.0

    # Initialiser les variables de calcul
    quantite_totale = 0
    valeur_totale = 0.0

    for mouvement in mouvements:
        if mouvement.type_mouvement in ["entree", "stock_initial", "ajustement_positif"]:
            # Pour les entrées, on ajoute la quantité et la valeur
            if mouvement.cout_unitaire is not None:
                quantite_totale += float(mouvement.quantite or 0)
                valeur_totale += float(mouvement.quantite or 0) * float(mouvement.cout_unitaire)
        elif mouvement.type_mouvement in ["sortie", "ajustement_negatif"]:
            # Pour les sorties, on retire la quantité (mais on ne modifie pas le coût moyen)
            quantite_totale -= float(mouvement.quantite or 0)
    
    # Calculer le coût moyen pondéré
    if quantite_totale > 0:
        cout_moyen = valeur_totale / quantite_totale
    else:
        cout_moyen = 0.0  # Si quantité totale est 0 ou négative, le coût moyen est 0
    
    return cout_moyen


def mettre_a_jour_cout_moyen_produit(db: Session, produit_id: str, station_id: str):
    """
    Met à jour le coût moyen d'un produit pour une station spécifique
    :param db: Session SQLAlchemy
    :param produit_id: ID du produit
    :param station_id: ID de la station
    """
    nouveau_cout_moyen = calculer_cout_moyen_pondere(db, produit_id, station_id)
    
    produit = db.query(Produit).filter(
        and_(
            Produit.id == produit_id,
            Produit.station_id == station_id
        )
    ).first()
    
    if produit:
        produit.cout_moyen = nouveau_cout_moyen
        db.commit()