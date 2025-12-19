from sqlalchemy.orm import Session
from ..models import MouvementStock, StockProduit
from decimal import Decimal
from datetime import datetime, timezone


def calculer_cout_moyen_pondere(db: Session, produit_id: str, station_id: str) -> Decimal:
    """
    Calcule le coût moyen pondéré pour un produit donné dans une station spécifique
    selon la formule: (quantité * coût + quantité_nouvelle * coût_nouveau) / (quantité + quantité_nouvelle)
    """
    # Récupérer tous les mouvements d'entrée pour ce produit dans cette station
    mouvements_entree = db.query(MouvementStock).filter(
        MouvementStock.produit_id == produit_id,
        MouvementStock.station_id == station_id,
        MouvementStock.type_mouvement.in_(['entree', 'ajustement'])
    ).order_by(MouvementStock.date_mouvement).all()

    # Initialiser les variables pour le calcul
    stock_cumule = Decimal('0')
    valeur_cumulee = Decimal('0')

    # Pour chaque mouvement d'entrée, recalculer le coût moyen pondéré
    for mouvement in mouvements_entree:
        if mouvement.cout_unitaire and mouvement.quantite:
            cout_total_entree = Decimal(str(mouvement.cout_unitaire)) * Decimal(str(mouvement.quantite))
            stock_cumule += Decimal(str(mouvement.quantite))
            valeur_cumulee += cout_total_entree

    # Si on a du stock, calculer le coût moyen pondéré
    if stock_cumule > 0:
        cout_moyen_pondere = valeur_cumulee / stock_cumule
    else:
        cout_moyen_pondere = Decimal('0')

    # Mettre à jour le stock produit avec le nouveau coût moyen
    stock_produit = db.query(StockProduit).filter(
        StockProduit.produit_id == produit_id,
        StockProduit.station_id == station_id
    ).first()
    if stock_produit:
        stock_produit.cout_moyen_pondere = cout_moyen_pondere
        stock_produit.date_dernier_calcul = datetime.now(timezone.utc)
        db.commit()

    return cout_moyen_pondere


def mettre_a_jour_stock_produit(db: Session, produit_id: str, station_id: str, quantite: float, type_mouvement: str):
    """
    Met à jour la quantité d'un produit en stock selon le type de mouvement
    """
    # Récupérer ou créer l'enregistrement de stock pour ce produit dans cette station
    stock_produit = db.query(StockProduit).filter(
        StockProduit.produit_id == produit_id,
        StockProduit.station_id == station_id
    ).first()

    if not stock_produit:
        # Créer un nouvel enregistrement de stock
        from sqlalchemy.dialects.postgresql import UUID
        import uuid
        stock_produit = StockProduit(
            id=uuid.uuid4(),
            produit_id=produit_id,
            station_id=station_id,
            quantite_theorique=Decimal('0'),
            quantite_reelle=Decimal('0')
        )
        db.add(stock_produit)
        db.flush()  # Pour s'assurer que l'ID est généré

    # Mettre à jour la quantité selon le type de mouvement
    quantite_decimal = Decimal(str(quantite))
    if type_mouvement == 'entree':
        stock_produit.quantite_theorique += quantite_decimal
    elif type_mouvement == 'sortie':
        stock_produit.quantite_theorique -= quantite_decimal
    elif type_mouvement == 'ajustement':
        # Pour un ajustement, on remplace la quantité
        stock_produit.quantite_theorique = quantite_decimal

    # Enregistrer les modifications
    db.commit()
    db.refresh(stock_produit)

    # Calculer et mettre à jour le coût moyen pondéré
    calculer_cout_moyen_pondere(db, produit_id, station_id)

    return stock_produit