from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
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
    date_mouvement: Optional[datetime] = None,
    transaction_source_id: Optional[str] = None,  # Référence à l'ID de la transaction source
    type_transaction_source: Optional[str] = None,  # Type de la transaction source ('achat', 'vente', etc.)
    prix_vente: Optional[float] = None,  # Prix de vente pour ce stock
    seuil_stock_min: Optional[float] = None  # Seuil minimum de stock
):
    """
    Enregistre un mouvement de stock. La mise à jour du stock théorique est effectuée automatiquement
    par un trigger PostgreSQL. Le coût moyen du produit est mis à jour après l'enregistrement.
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
        reference_origine=reference_origine,
        transaction_source_id=transaction_source_id,  # Référence à la transaction source
        type_transaction_source=type_transaction_source  # Type de la transaction source
    )

    db.add(mouvement)
    db.commit()
    db.refresh(mouvement)

    # Mettre à jour le coût moyen du produit
    mettre_a_jour_cout_moyen_produit(db, produit_id, station_id)

    # Si un prix de vente est fourni, le mettre à jour dans la table stock_produit
    if prix_vente is not None:
        from ..models.stock import StockProduit
        from sqlalchemy import and_
        from decimal import Decimal

        # Récupérer ou créer l'enregistrement de stock pour ce produit et cette station
        stock_produit = db.query(StockProduit).filter(
            and_(
                StockProduit.produit_id == produit_id,
                StockProduit.station_id == station_id
            )
        ).first()

        if stock_produit:
            stock_produit.prix_vente = Decimal(str(prix_vente))
            db.commit()

    # Si un seuil de stock minimum est fourni, le mettre à jour dans la table stock_produit
    if seuil_stock_min is not None:
        from ..models.stock import StockProduit
        from sqlalchemy import and_
        from decimal import Decimal

        # Récupérer ou créer l'enregistrement de stock pour ce produit et cette station
        stock_produit = db.query(StockProduit).filter(
            and_(
                StockProduit.produit_id == produit_id,
                StockProduit.station_id == station_id
            )
        ).first()

        if stock_produit:
            stock_produit.seuil_stock_min = Decimal(str(seuil_stock_min))
            db.commit()

    return mouvement


def mettre_a_jour_stock_produit_automatiquement(
    db: Session,
    produit_id: str,
    station_id: str,
    type_mouvement: str,
    quantite: float,
    cout_unitaire: Optional[float] = None
):
    """
    Met à jour automatiquement la quantité du stock dans la table stock_produit
    selon le type de mouvement.

    Args:
        db: Session de base de données
        produit_id: ID du produit concerné
        station_id: ID de la station concernée
        type_mouvement: Type de mouvement ('entree', 'sortie', 'ajustement', 'stock_initial', etc.)
        quantite: Quantité concernée par le mouvement
        cout_unitaire: Coût unitaire du mouvement (optionnel)
    """
    # Récupérer ou créer l'enregistrement de stock pour ce produit et cette station
    stock = db.query(StockProduit).filter(
        and_(
            StockProduit.produit_id == produit_id,
            StockProduit.station_id == station_id
        )
    ).first()

    if stock is None:
        # Créer un nouvel enregistrement de stock s'il n'existe pas
        from sqlalchemy.dialects.postgresql import UUID
        import uuid
        stock = StockProduit(
            id=uuid.uuid4(),
            produit_id=produit_id,
            station_id=station_id,
            quantite_theorique=Decimal('0'),
            quantite_reelle=Decimal('0'),
            cout_moyen_pondere=Decimal('0')
        )
        db.add(stock)
        db.flush()  # Pour s'assurer que l'ID est généré

    # Convertir la quantité en Decimal pour des calculs précis
    quantite_decimal = Decimal(str(quantite))

    # Mettre à jour la quantité selon le type de mouvement
    if type_mouvement in ['entree', 'stock_initial', 'ajustement_positif', 'inventaire_positif']:
        stock.quantite_theorique += quantite_decimal
    elif type_mouvement in ['sortie', 'ajustement_negatif', 'inventaire_negatif']:
        stock.quantite_theorique -= quantite_decimal
    elif type_mouvement == 'ajustement':
        # Pour un ajustement, on remplace la quantité
        stock.quantite_theorique = quantite_decimal
    else:
        # Pour d'autres types de mouvements, ignorer ou lever une exception selon les besoins
        raise ValueError(f"Type de mouvement inconnu: {type_mouvement}")

    # S'assurer que la quantité ne soit pas négative
    if stock.quantite_theorique < 0:
        stock.quantite_theorique = 0

    # Mettre à jour la date du dernier calcul
    stock.date_dernier_calcul = datetime.now(timezone.utc)

    # Mettre à jour le coût moyen pondéré si un coût unitaire est fourni
    if cout_unitaire is not None:
        # Calculer le nouveau coût moyen pondéré
        cout_unitaire_decimal = Decimal(str(cout_unitaire))

        # Calculer la valeur totale avant le mouvement
        valeur_avant = stock.quantite_theorique * stock.cout_moyen_pondere - quantite_decimal * cout_unitaire_decimal

        # Calculer la quantité avant le mouvement
        quantite_avant = stock.quantite_theorique - quantite_decimal

        # Calculer le nouveau coût moyen pondéré
        if quantite_avant > 0:
            cout_moyen_avant = valeur_avant / quantite_avant
        else:
            cout_moyen_avant = stock.cout_moyen_pondere  # Utiliser l'ancien coût moyen si pas de stock avant

        # Calculer le nouveau coût moyen pondéré après le mouvement
        valeur_apres = valeur_avant + quantite_decimal * cout_unitaire_decimal
        quantite_apres = stock.quantite_theorique

        if quantite_apres > 0:
            stock.cout_moyen_pondere = valeur_apres / quantite_apres
        else:
            stock.cout_moyen_pondere = Decimal('0')

    # Enregistrer les modifications
    db.commit()
    db.refresh(stock)

    return stock


def annuler_mouvements_stock_transaction(
    db: Session,
    transaction_source_id: str,
    type_transaction_source: str
):
    """
    Annule tous les mouvements de stock liés à une transaction spécifique en mettant à jour leur statut.
    La mise à jour des stocks est effectuée automatiquement par un trigger PostgreSQL.

    Args:
        db: Session de base de données
        transaction_source_id: ID de la transaction source à annuler
        type_transaction_source: Type de la transaction source ('achat', 'vente', etc.)
    """
    # Récupérer tous les mouvements de stock liés à cette transaction
    mouvements = db.query(MouvementStock).filter(
        MouvementStock.transaction_source_id == transaction_source_id,
        MouvementStock.type_transaction_source == type_transaction_source
    ).all()

    for mouvement in mouvements:
        # Marquer le mouvement comme annulé pour déclencher le trigger
        mouvement.statut = 'annulé'

    db.commit()


def annuler_stock_initial(
    db: Session,
    produit_id: str,
    station_id: str,
    utilisateur_id: str,
    reference_origine: str = "Annulation Stock Initial"
):
    """
    Annule un stock initial en enregistrant un mouvement inverse et en mettant à jour le statut des mouvements existants.
    La mise à jour des stocks est effectuée automatiquement par un trigger PostgreSQL.

    Args:
        db: Session de base de données
        produit_id: ID du produit concerné
        station_id: ID de la station concernée
        utilisateur_id: ID de l'utilisateur effectuant l'annulation
        reference_origine: Référence pour l'annulation
    """
    # Récupérer tous les mouvements liés au stock initial pour ce produit et cette station
    # avec le type "stock_initial"
    mouvements = db.query(MouvementStock).filter(
        MouvementStock.produit_id == produit_id,
        MouvementStock.station_id == station_id,
        MouvementStock.type_mouvement == "stock_initial"
    ).all()

    if not mouvements:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Aucun mouvement de stock initial trouvé")

    # Calculer la quantité totale du stock initial
    quantite_totale = sum(m.quantite for m in mouvements)

    # Créer un mouvement inverse pour annuler le stock initial
    mouvement_inverse = MouvementStock(
        produit_id=produit_id,
        station_id=station_id,
        type_mouvement="annulation_stock_initial",
        quantite=-quantite_totale,  # Quantité totale négative
        cout_unitaire=None,  # Pas de coût unitaire pour l'annulation
        utilisateur_id=utilisateur_id,
        module_origine="stock_initial",
        reference_origine=reference_origine,
        statut="validé"  # Le mouvement inverse est validé
    )

    db.add(mouvement_inverse)

    # Mettre à jour le statut des mouvements originaux à "annulé"
    for mouvement in mouvements:
        mouvement.statut = "annulé"

    db.commit()

    return mouvement_inverse