from sqlalchemy.orm import Session
from api.models.compagnie import Cuve, EtatInitialCuve, MouvementStockCuve
from api.models.stock_carburant import StockCarburant
from api.models.prix_carburant import PrixCarburant
from datetime import datetime
from uuid import uuid4

async def update_etat_initial_cuve_service(
    cuve_id: str,
    etat_initial_data,
    volume_calcule,
    db: Session,
    current_user
):
    """
    Mettre à jour l'état initial d'une cuve
    """
    # Récupérer la cuve pour obtenir le carburant_id et station_id
    cuve = db.query(Cuve).filter(Cuve.id == cuve_id).first()
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
        cout_moyen = getattr(etat_initial_data, 'cout_moyen', 0) or 0
        prix_vente = getattr(etat_initial_data, 'prix_vente', 0) or 0

    # Récupérer l'état initial existant
    etat_initial = db.query(EtatInitialCuve).filter(EtatInitialCuve.cuve_id == cuve_id).first()

    if not etat_initial:
        raise ValueError("L'état initial de la cuve n'existe pas")

    # Vérifier qu'il n'y a pas d'autres mouvements que ceux liés à l'état initial
    # On ne considère que les mouvements non liés à l'état initial après la date d'initialisation
    from sqlalchemy import text

    # Obtenir le nombre total de mouvements et le nombre de mouvements autorisés (liés à l'état initial) après la date d'initialisation
    result = db.execute(text("""
        SELECT COUNT(*), COUNT(*) FILTER (WHERE type_mouvement IN ('ajustement_positif', 'ajustement_negatif', 'stock_initial'))
        FROM mouvement_stock_cuve
        WHERE cuve_id = :cuve_id
        AND est_actif = true
        AND date_mouvement > :date_initialisation
    """), {"cuve_id": cuve_id, "date_initialisation": etat_initial.date_initialisation})

    count_total, count_ajustements = result.fetchone()

    print(f"Mouvements après la date d'initialisation pour la cuve {cuve_id} - Total: {count_total}, Ajustements + stock_initial: {count_ajustements}")

    if count_total > count_ajustements:
        raise ValueError("Impossible de modifier l'état initial : des mouvements supplémentaires existent après la date d'initialisation")

    # Créer un mouvement inverse pour annuler l'état initial précédent
    mouvement_inverse = MouvementStockCuve(
        cuve_id=cuve_id,
        type_mouvement="ajustement_negatif",
        quantite=etat_initial.volume_initial_calcule,
        date_mouvement=datetime.utcnow(),
        utilisateur_id=current_user.id,
        reference_origine="CORR",
        module_origine="etat_initial_cuve"
    )

    db.add(mouvement_inverse)

    # Mettre à jour l'état initial
    if etat_initial_data.hauteur_jauge_initiale is not None:
        etat_initial.hauteur_jauge_initiale = etat_initial_data.hauteur_jauge_initiale
    etat_initial.volume_initial_calcule = volume_calcule

    # Mettre à jour ou créer le stock carburant
    stock_carburant = db.query(StockCarburant).filter(
        StockCarburant.cuve_id == cuve_id
    ).first()

    if stock_carburant:
        # Mettre à jour l'enregistrement existant
        stock_carburant.quantite_theorique = volume_calcule
        stock_carburant.quantite_reelle = volume_calcule
        stock_carburant.date_dernier_calcul = datetime.utcnow()
        stock_carburant.cout_moyen_pondere = cout_moyen
        stock_carburant.prix_vente = prix_vente
        if hasattr(etat_initial_data, 'seuil_stock_min') and etat_initial_data.seuil_stock_min is not None:
            stock_carburant.seuil_stock_min = etat_initial_data.seuil_stock_min
    else:
        # Créer un nouvel enregistrement dans la table stock_carburant
        stock_carburant = StockCarburant(
            cuve_id=cuve_id,
            quantite_theorique=volume_calcule,
            quantite_reelle=volume_calcule,
            date_dernier_calcul=datetime.utcnow(),
            cout_moyen_pondere=cout_moyen,
            prix_vente=prix_vente,
            seuil_stock_min=getattr(etat_initial_data, 'seuil_stock_min', 0) or 0
        )
        db.add(stock_carburant)

    # Créer un nouveau mouvement de stock initial avec les nouvelles valeurs
    nouveau_mouvement_initial = MouvementStockCuve(
        cuve_id=cuve_id,
        type_mouvement="stock_initial",
        quantite=volume_calcule,
        date_mouvement=datetime.utcnow(),
        utilisateur_id=current_user.id,
        reference_origine="INIT",
        module_origine="etat_initial_cuve"
    )

    db.add(nouveau_mouvement_initial)
    db.commit()
    db.refresh(etat_initial)

    return etat_initial


async def delete_etat_initial_cuve_service(
    cuve_id: str,
    db: Session,
    current_user
):
    """
    Supprimer l'état initial d'une cuve
    """
    # Récupérer l'état initial
    etat_initial = db.query(EtatInitialCuve).filter(EtatInitialCuve.cuve_id == cuve_id).first()

    if not etat_initial:
        raise ValueError("L'état initial de la cuve n'existe pas")

    # Vérifier qu'il n'y a pas d'autres mouvements que ceux liés à l'état initial
    mouvements = db.query(MouvementStockCuve).filter(
        MouvementStockCuve.cuve_id == cuve_id
    ).all()

    # Vérifier qu'il n'y a que des mouvements liés à l'état initial (stock_initial, ajustement_positif, ajustement_negatif)
    mouvements_autorises = [m for m in mouvements if m.type_mouvement in ["stock_initial", "ajustement_positif", "ajustement_negatif"]]
    if len(mouvements) != len(mouvements_autorises):
        raise ValueError("Impossible d'annuler l'état initial : des mouvements supplémentaires existent")

    # Supprimer le mouvement de stock initial
    for mouvement in mouvements:
        db.delete(mouvement)

    # Supprimer le couple dans la table stock_carburant
    stock_carburant = db.query(StockCarburant).filter(
        StockCarburant.cuve_id == cuve_id
    ).first()

    if stock_carburant:
        db.delete(stock_carburant)

    # Supprimer l'état initial
    db.delete(etat_initial)
    db.commit()

    return {"message": "État initial annulé avec succès"}


async def create_etat_initial_cuve_service(
    cuve_id: str,
    etat_initial_data,
    volume_calcule,
    db: Session,
    current_user
):
    """
    Créer l'état initial d'une cuve
    """
    # Récupérer la cuve pour obtenir le carburant_id et station_id
    cuve = db.query(Cuve).filter(Cuve.id == cuve_id).first()
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
        cout_moyen = getattr(etat_initial_data, 'cout_moyen', 0) or 0
        prix_vente = getattr(etat_initial_data, 'prix_vente', 0) or 0

    # Créer l'état initial
    nouvel_etat_initial = EtatInitialCuve(
        cuve_id=cuve_id,
        hauteur_jauge_initiale=etat_initial_data.hauteur_jauge_initiale,
        volume_initial_calcule=volume_calcule,
        date_initialisation=datetime.utcnow(),
        utilisateur_id=current_user.id,
        verrouille=False
    )

    db.add(nouvel_etat_initial)
    db.flush()  # Pour obtenir l'ID avant la suite des opérations

    # Créer ou mettre à jour l'enregistrement dans la table stock_carburant
    stock_carburant = db.query(StockCarburant).filter(
        StockCarburant.cuve_id == cuve_id
    ).first()

    if stock_carburant:
        # Mettre à jour l'enregistrement existant
        stock_carburant.quantite_theorique = volume_calcule
        stock_carburant.quantite_reelle = volume_calcule
        stock_carburant.date_dernier_calcul = datetime.utcnow()
        stock_carburant.cout_moyen_pondere = cout_moyen
        stock_carburant.prix_vente = prix_vente
        if hasattr(etat_initial_data, 'seuil_stock_min') and etat_initial_data.seuil_stock_min is not None:
            stock_carburant.seuil_stock_min = etat_initial_data.seuil_stock_min
    else:
        # Créer un nouvel enregistrement dans la table stock_carburant
        stock_carburant = StockCarburant(
            cuve_id=cuve_id,
            quantite_theorique=volume_calcule,
            quantite_reelle=volume_calcule,
            date_dernier_calcul=datetime.utcnow(),
            cout_moyen_pondere=cout_moyen,
            prix_vente=prix_vente,
            seuil_stock_min=getattr(etat_initial_data, 'seuil_stock_min', 0) or 0
        )
        db.add(stock_carburant)
        # Valider immédiatement pour s'assurer que l'enregistrement est disponible pour le trigger
        db.commit()

    # Créer un mouvement de stock initial
    mouvement_initial = MouvementStockCuve(
        cuve_id=cuve_id,
        type_mouvement="stock_initial",
        quantite=volume_calcule,
        date_mouvement=datetime.utcnow(),
        utilisateur_id=current_user.id,
        reference_origine="INIT",
        module_origine="etat_initial_cuve"
    )

    db.add(mouvement_initial)
    db.commit()
    db.refresh(nouvel_etat_initial)

    return nouvel_etat_initial