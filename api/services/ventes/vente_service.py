from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from datetime import datetime
from uuid import UUID
from ...models import Vente as VenteModel, VenteDetail as VenteDetailModel, Station
from ...models import VenteCarburant as VenteCarburantModel, CreanceEmploye as CreanceEmployeModel, PrixCarburant
from ...models.tresorerie import TresorerieStation as TresorerieStationModel, MouvementTresorerie as MouvementTresorerieModel
from ...ventes import schemas


def get_ventes(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les ventes appartenant aux stations de l'utilisateur"""
    ventes = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return ventes


def create_vente(db: Session, current_user, vente: schemas.VenteCreate):
    """Crée une nouvelle vente avec ses détails"""
    # Vérifier que la trésorerie station appartient à l'utilisateur
    trésorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == vente.trésorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not trésorerie_station:
        raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

    # Calculate total amount from details
    total_amount = sum(detail.montant for detail in vente.details)

    # Create the main vente record
    db_vente = VenteModel(
        client_id=vente.client_id,
        date=vente.date,
        montant_total=total_amount,
        statut=vente.statut,
        type_vente=vente.type_vente,
        trésorerie_station_id=vente.trésorerie_station_id,
        numero_piece_comptable=vente.numero_piece_comptable,
        compagnie_id=current_user.compagnie_id
    )

    db.add(db_vente)
    db.flush()  # To get the ID before committing

    # Create the details
    for detail in vente.details:
        db_detail = VenteDetailModel(
            vente_id=db_vente.id,  # Utilisation directe de l'ID objet SQLAlchemy
            produit_id=detail.produit_id,
            quantite=detail.quantite,
            prix_unitaire=detail.prix_unitaire,
            montant=detail.montant,
            remise=detail.remise
        )
        db.add(db_detail)

    # Créer un mouvement de trésorerie pour enregistrer l'entrée d'argent
    mouvement_entree = MouvementTresorerieModel(
        trésorerie_station_id=vente.trésorerie_station_id,
        type_mouvement="entrée",
        montant=total_amount,
        date_mouvement=datetime.utcnow(),
        description=f"Vente enregistrée (ID: {db_vente.id})",
        module_origine="ventes",
        reference_origine=f"VTE-{db_vente.id}",
        utilisateur_id=current_user.id
    )
    db.add(mouvement_entree)

    # Mettre à jour le solde de la trésorerie
    from ...services.tresoreries import mettre_a_jour_solde_tresorerie
    mettre_a_jour_solde_tresorerie(db, vente.trésorerie_station_id)

    db.commit()
    db.refresh(db_vente)

    return db_vente


def get_vente_by_id(db: Session, current_user, vente_id: UUID):
    """Récupère une vente spécifique par son ID"""
    vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")
    return vente


def update_vente(db: Session, current_user, vente_id: UUID, vente: schemas.VenteUpdate):
    """Met à jour une vente existante"""
    db_vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    update_data = vente.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vente, field, value)

    db.commit()
    db.refresh(db_vente)
    return db_vente


def delete_vente(db: Session, current_user, vente_id: UUID):
    """Supprime une vente existante"""
    vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    # Delete related details first
    db.query(VenteDetailModel).filter(VenteDetailModel.vente_id == vente_id).delete()

    db.delete(vente)
    db.commit()
    return {"message": "Vente deleted successfully"}


def get_vente_details(db: Session, current_user, vente_id: UUID, skip: int = 0, limit: int = 100):
    """Récupère les détails d'une vente spécifique"""
    # Vérifier que la vente appartient à l'utilisateur
    vente = db.query(VenteModel).join(
        Station,
        VenteModel.station_id == Station.id
    ).filter(
        VenteModel.id == vente_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    details = db.query(VenteDetailModel).filter(VenteDetailModel.vente_id == vente_id).offset(skip).limit(limit).all()
    return details


def get_ventes_carburant(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les ventes de carburant appartenant aux stations de l'utilisateur"""
    ventes_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return ventes_carburant


def create_vente_carburant(db: Session, current_user, vente_carburant: schemas.VenteCarburantCreate):
    """Crée une nouvelle vente de carburant"""
    # Vérifier que la station appartient à l'utilisateur
    station = db.query(Station).filter(
        Station.id == vente_carburant.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=403, detail="Station does not belong to your company")

    # Vérifier que la trésorerie station appartient à l'utilisateur si elle est spécifiée
    trésorerie_station = None
    if vente_carburant.trésorerie_station_id:
        trésorerie_station = db.query(TresorerieStationModel).join(
            Station,
            TresorerieStationModel.station_id == Station.id
        ).filter(
            TresorerieStationModel.id == vente_carburant.trésorerie_station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not trésorerie_station:
            raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

    # Récupérer les informations de la cuve pour déterminer le carburant_id
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT c.carburant_id, s.id as station_id
        FROM cuve c
        JOIN station s ON c.station_id = s.id
        WHERE c.id = :cuve_id
    """), {"cuve_id": vente_carburant.cuve_id})

    cuve_data = result.fetchone()

    if not cuve_data or not cuve_data.carburant_id:
        raise HTTPException(status_code=404, detail="Carburant de la cuve non trouvé")

    # Déterminer le carburant_id à utiliser
    carburant_id = vente_carburant.carburant_id or cuve_data.carburant_id

    # Récupérer le prix de vente depuis la table prix_carburant
    prix_carburant = db.query(PrixCarburant).filter(
        PrixCarburant.carburant_id == carburant_id,
        PrixCarburant.station_id == vente_carburant.station_id
    ).first()

    if not prix_carburant or not prix_carburant.prix_vente:
        raise HTTPException(status_code=404, detail="Prix de vente non trouvé pour ce carburant et cette station")

    prix_unitaire = prix_carburant.prix_vente

    # Calculer le montant total
    montant_total = vente_carburant.quantite_vendue * prix_unitaire

    # Créer l'enregistrement de vente de carburant
    db_vente_carburant = VenteCarburantModel(
        station_id=vente_carburant.station_id,
        cuve_id=vente_carburant.cuve_id,
        pistolet_id=vente_carburant.pistolet_id,
        trésorerie_station_id=vente_carburant.trésorerie_station_id,  # Ajout de la référence à la trésorerie
        quantite_vendue=vente_carburant.quantite_vendue,
        prix_unitaire=prix_unitaire,
        montant_total=montant_total,
        date_vente=vente_carburant.date_vente,
        index_initial=vente_carburant.index_initial,
        index_final=vente_carburant.index_final,
        pompiste=vente_carburant.pompiste,
        qualite_marshalle_id=vente_carburant.qualite_marshalle_id,
        montant_paye=vente_carburant.montant_paye,
        mode_paiement=vente_carburant.mode_paiement,
        utilisateur_id=vente_carburant.utilisateur_id
    )

    # Si le montant payé est inférieur au montant dû, créer une créance employé
    if vente_carburant.montant_paye < montant_total:
        montant_creance = montant_total - vente_carburant.montant_paye

        creance_employe = CreanceEmployeModel(
            vente_carburant_id=db_vente_carburant.id,
            pompiste=vente_carburant.pompiste,
            montant_du=montant_creance,
            montant_paye=vente_carburant.montant_paye,
            solde_creance=montant_creance,
            created_at=vente_carburant.date_vente,
            utilisateur_gestion_id=vente_carburant.utilisateur_id
        )

        db.add(creance_employe)
        db_vente_carburant.creance_employe_id = creance_employe.id

    db.add(db_vente_carburant)
    db.commit()
    db.refresh(db_vente_carburant)

    # Si la vente est effectuée en espèces et qu'une trésorerie est spécifiée, enregistrer le mouvement
    if (vente_carburant.mode_paiement == "espèce" or vente_carburant.mode_paiement == "chèque") and vente_carburant.trésorerie_station_id:
        # Créer un mouvement de trésorerie pour enregistrer l'entrée d'argent
        mouvement_entree = MouvementTresorerieModel(
            trésorerie_station_id=vente_carburant.trésorerie_station_id,
            type_mouvement="entrée",
            montant=vente_carburant.montant_paye,
            date_mouvement=datetime.utcnow(),
            description=f"Vente carburant enregistrée (ID: {db_vente_carburant.id})",
            module_origine="ventes_carburant",
            reference_origine=f"VTE-CB-{db_vente_carburant.id}",
            utilisateur_id=current_user.id
        )
        db.add(mouvement_entree)

        # Mettre à jour le solde de la trésorerie
        from ...services.tresoreries import mettre_a_jour_solde_tresorerie
        mettre_a_jour_solde_tresorerie(db, vente_carburant.trésorerie_station_id)

    db.commit()

    return db_vente_carburant


def get_vente_carburant_by_id(db: Session, current_user, vente_carburant_id: UUID):
    """Récupère une vente de carburant spécifique par son ID"""
    vente_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        VenteCarburantModel.id == vente_carburant_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")
    return vente_carburant


def update_vente_carburant(db: Session, current_user, vente_carburant_id: UUID, vente_carburant: schemas.VenteCarburantUpdate):
    """Met à jour une vente de carburant existante"""
    db_vente_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        VenteCarburantModel.id == vente_carburant_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")

    update_data = vente_carburant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vente_carburant, field, value)

    db.commit()
    db.refresh(db_vente_carburant)
    return db_vente_carburant


def delete_vente_carburant(db: Session, current_user, vente_carburant_id: UUID):
    """Supprime une vente de carburant existante"""
    vente_carburant = db.query(VenteCarburantModel).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        VenteCarburantModel.id == vente_carburant_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")

    db.delete(vente_carburant)
    db.commit()
    return {"message": "Vente carburant deleted successfully"}


def get_creances_employes(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les créances employés appartenant aux stations de l'utilisateur"""
    from ...models import VenteCarburant
    creances = db.query(CreanceEmployeModel).join(
        VenteCarburant,
        CreanceEmployeModel.vente_carburant_id == VenteCarburant.id
    ).join(
        Station,
        VenteCarburant.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return creances


def get_creance_employe_by_id(db: Session, current_user, creance_id: UUID):
    """Récupère une créance employé spécifique par son ID"""
    from ...models import VenteCarburant
    creance = db.query(CreanceEmployeModel).join(
        VenteCarburantModel,
        CreanceEmployeModel.vente_carburant_id == VenteCarburantModel.id
    ).join(
        Station,
        VenteCarburantModel.station_id == Station.id
    ).filter(
        CreanceEmployeModel.id == creance_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not creance:
        raise HTTPException(status_code=404, detail="Creance employé not found")
    return creance