from sqlalchemy.orm import Session
from api.models.compagnie import Cuve, EtatInitialCuve, MouvementStockCuve
from api.models.stock_carburant import StockCarburant
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
        stock_carburant.cout_moyen_pondere = stock_initial_data.cout_moyen or 0
        stock_carburant.prix_vente = stock_initial_data.prix_vente or 0
        stock_carburant.seuil_stock_min = stock_initial_data.seuil_stock_min or 0
    else:
        # Créer un nouveau stock carburant
        stock_carburant = StockCarburant(
            cuve_id=stock_initial_data.cuve_id,
            quantite_theorique=volume_calcule,
            quantite_reelle=volume_calcule,
            date_dernier_calcul=datetime.utcnow(),
            cout_moyen_pondere=stock_initial_data.cout_moyen or 0,
            prix_vente=stock_initial_data.prix_vente or 0,
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