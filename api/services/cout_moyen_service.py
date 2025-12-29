from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.produit import Produit
from ..models.stock import StockProduit
from ..models.mouvement_stock import MouvementStock
from decimal import Decimal
from datetime import datetime, timezone


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
    quantite_totale = Decimal('0')
    valeur_totale = Decimal('0')

    for mouvement in mouvements:
        if mouvement.type_mouvement in ["entree", "stock_initial", "ajustement_positif"]:
            # Pour les entrées, on ajoute la quantité et la valeur
            if mouvement.cout_unitaire is not None:
                quantite_mvt = Decimal(str(mouvement.quantite or 0))
                cout_mvt = Decimal(str(mouvement.cout_unitaire))

                quantite_totale += quantite_mvt
                valeur_totale += quantite_mvt * cout_mvt
        elif mouvement.type_mouvement in ["sortie", "ajustement_negatif"]:
            # Pour les sorties, on retire la quantité (mais on ne modifie pas le coût moyen)
            quantite_totale -= Decimal(str(mouvement.quantite or 0))

    # Calculer le coût moyen pondéré
    if quantite_totale > 0:
        cout_moyen = float(valeur_totale / quantite_totale)
    else:
        cout_moyen = 0.0  # Si quantité totale est 0 ou négative, le coût moyen est 0

    return cout_moyen


def mettre_a_jour_cout_moyen_produit(db: Session, produit_id: str, station_id: str):
    """
    Met à jour le coût moyen d'un produit pour une station spécifique dans la table stock_produit
    :param db: Session SQLAlchemy
    :param produit_id: ID du produit
    :param station_id: ID de la station
    """
    nouveau_cout_moyen = calculer_cout_moyen_pondere(db, produit_id, station_id)

    # Mettre à jour le champ cout_moyen_pondere dans la table stock_produit
    stock_produit = db.query(StockProduit).filter(
        and_(
            StockProduit.produit_id == produit_id,
            StockProduit.station_id == station_id
        )
    ).first()

    if stock_produit:
        stock_produit.cout_moyen_pondere = Decimal(str(nouveau_cout_moyen))
        stock_produit.date_dernier_calcul = datetime.now(timezone.utc)
        db.commit()
    else:
        # Si le stock_produit n'existe pas encore, on le crée avec le coût moyen
        from sqlalchemy.dialects.postgresql import UUID
        import uuid
        stock_produit = StockProduit(
            id=uuid.uuid4(),
            produit_id=produit_id,
            station_id=station_id,
            cout_moyen_pondere=Decimal(str(nouveau_cout_moyen)),
            date_dernier_calcul=datetime.now(timezone.utc)
        )
        db.add(stock_produit)
        db.commit()


def mettre_a_jour_cout_moyen_produit_initial(db: Session, produit_id: str, station_id: str, cout_unitaire_initial: float):
    """
    Met à jour le coût moyen d'un produit pour une station spécifique lors de la création d'un stock initial
    :param db: Session SQLAlchemy
    :param produit_id: ID du produit
    :param station_id: ID de la station
    :param cout_unitaire_initial: Coût unitaire initial à enregistrer comme coût moyen pondéré
    """
    # Mettre à jour le champ cout_moyen_pondere dans la table stock_produit
    stock_produit = db.query(StockProduit).filter(
        and_(
            StockProduit.produit_id == produit_id,
            StockProduit.station_id == station_id
        )
    ).first()

    if stock_produit:
        stock_produit.cout_moyen_pondere = Decimal(str(cout_unitaire_initial))
        stock_produit.date_dernier_calcul = datetime.now(timezone.utc)
        db.commit()
    else:
        # Si le stock_produit n'existe pas encore, on le crée avec le coût moyen initial
        from sqlalchemy.dialects.postgresql import UUID
        import uuid
        stock_produit = StockProduit(
            id=uuid.uuid4(),
            produit_id=produit_id,
            station_id=station_id,
            cout_moyen_pondere=Decimal(str(cout_unitaire_initial)),
            date_dernier_calcul=datetime.now(timezone.utc)
        )
        db.add(stock_produit)
        db.commit()