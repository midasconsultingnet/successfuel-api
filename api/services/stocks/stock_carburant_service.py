from sqlalchemy.orm import Session
from api.models.compagnie import Cuve, EtatInitialCuve, MouvementStockCuve
from api.models.stock_carburant import StockCarburant
from api.models.prix_carburant import PrixCarburant
from datetime import datetime
from uuid import uuid4


async def creer_stock_initial_carburant(
    stock_initial_data,
    volume_calcule,
    db: Session,
    current_user
):
    """
    Créer un stock initial pour une cuve de carburant
    """
    # Récupérer la cuve pour obtenir le carburant_id et station_id
    cuve = db.query(Cuve).filter(Cuve.id == stock_initial_data.cuve_id).first()
    if not cuve:
        raise ValueError("Cuve non trouvée")

    # Récupérer les prix du carburant pour cette station
    prix_carburant = db.query(PrixCarburant).filter(
        PrixCarburant.carburant_id == cuve.carburant_id,
        PrixCarburant.station_id == cuve.station_id
    ).first()

    # Utiliser les prix du carburant s'ils existent, sinon utiliser les valeurs du payload
    cout_moyen = 0
    prix_vente = 0

    if prix_carburant:
        cout_moyen = float(prix_carburant.prix_achat) if prix_carburant.prix_achat else 0
        prix_vente = float(prix_carburant.prix_vente) if prix_carburant.prix_vente else 0
    else:
        # Si aucun prix n'est trouvé, on peut utiliser les valeurs du payload comme fallback
        cout_moyen = stock_initial_data.cout_moyen or 0
        prix_vente = stock_initial_data.prix_vente or 0

    # Créer l'enregistrement d'état initial
    etat_initial = EtatInitialCuve(
        cuve_id=stock_initial_data.cuve_id,
        hauteur_jauge_initiale=stock_initial_data.hauteur_jauge_initiale,
        volume_calcule=volume_calcule,
        utilisateur_creation_id=current_user.id
    )

    db.add(etat_initial)
    db.commit()
    db.refresh(etat_initial)

    # Créer ou mettre à jour le stock carburant correspondant
    stock_carburant = db.query(StockCarburant).filter(
        StockCarburant.cuve_id == stock_initial_data.cuve_id
    ).first()

    if stock_carburant:
        # Mettre à jour le stock existant
        stock_carburant.quantite_theorique = volume_calcule
        stock_carburant.quantite_reelle = volume_calcule
        stock_carburant.date_dernier_calcul = datetime.utcnow()
        stock_carburant.cout_moyen_pondere = cout_moyen
        stock_carburant.prix_vente = prix_vente
        stock_carburant.seuil_stock_min = stock_initial_data.seuil_stock_min or 0
    else:
        # Créer un nouveau stock carburant
        stock_carburant = StockCarburant(
            cuve_id=stock_initial_data.cuve_id,
            quantite_theorique=volume_calcule,
            quantite_reelle=volume_calcule,
            date_dernier_calcul=datetime.utcnow(),
            cout_moyen_pondere=cout_moyen,
            prix_vente=prix_vente,
            seuil_stock_min=stock_initial_data.seuil_stock_min or 0
        )
        db.add(stock_carburant)

    # Créer un mouvement de stock initial
    mouvement_initial = MouvementStockCuve(
        cuve_id=stock_initial_data.cuve_id,
        type_mouvement="stock_initial",
        quantite=volume_calcule,
        utilisateur_id=current_user.id,
        description="Stock initial de carburant"
    )

    db.add(mouvement_initial)
    db.commit()
    db.refresh(stock_carburant)

    return stock_carburant