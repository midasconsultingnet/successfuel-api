from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from ...models.tresorerie import (
    Tresorerie as TresorerieModel,
    TresorerieStation as TresorerieStationModel,
    MouvementTresorerie as MouvementTresorerieModel,
    TransfertTresorerie as TransfertTresorerieModel,
    EtatInitialTresorerie as EtatInitialTresorerieModel
)
from ...models import Station
from ...tresoreries import schemas
import uuid
from datetime import datetime


def mettre_a_jour_solde_tresorerie(db: Session, trésorerie_station_id: uuid.UUID):
    """Met à jour le solde actuel d'une trésorerie station en fonction des mouvements"""
    # Récupérer la trésorerie station
    trésorerie_station = db.query(TresorerieStationModel).filter(
        TresorerieStationModel.id == trésorerie_station_id
    ).first()

    if not trésorerie_station:
        raise HTTPException(status_code=404, detail="Trésorerie station non trouvée")

    # Calculer le solde à partir des mouvements validés
    entrees = db.query(MouvementTresorerieModel).filter(
        MouvementTresorerieModel.trésorerie_station_id == trésorerie_station_id,
        MouvementTresorerieModel.type_mouvement == "entrée",
        MouvementTresorerieModel.statut == "validé"
    ).with_entities(db.func.sum(MouvementTresorerieModel.montant)).scalar() or 0

    sorties = db.query(MouvementTresorerieModel).filter(
        MouvementTresorerieModel.trésorerie_station_id == trésorerie_station_id,
        MouvementTresorerieModel.type_mouvement == "sortie",
        MouvementTresorerieModel.statut == "validé"
    ).with_entities(db.func.sum(MouvementTresorerieModel.montant)).scalar() or 0

    # Calculer le solde
    solde_actuel = float(trésorerie_station.solde_initial) + float(entrees) - float(sorties)
    trésorerie_station.solde_actuel = solde_actuel

    db.commit()
    return solde_actuel


def get_tresoreries_station(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les trésoreries station appartenant aux stations de l'utilisateur"""
    tresoreries_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return tresoreries_station


def get_tresoreries_station_by_station(db: Session, current_user, station_id: uuid.UUID):
    """Récupère les trésoreries pour une station spécifique"""
    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=403, detail="Station does not belong to your company")

    # Récupérer les trésoreries de cette station spécifique
    tresoreries_station = db.query(TresorerieStationModel).filter(
        TresorerieStationModel.station_id == station_id
    ).all()

    return tresoreries_station


def get_tresoreries(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les trésoreries appartenant à la compagnie de l'utilisateur"""
    tresoreries = db.query(TresorerieModel).filter(
        TresorerieModel.compagnie_id == current_user.compagnie_id,
        TresorerieModel.statut != "supprimé"  # Exclure les trésoreries supprimées
    ).offset(skip).limit(limit).all()

    return tresoreries


def create_tresorerie(db: Session, current_user, tresorerie: schemas.TresorerieCreate):
    """Crée une nouvelle trésorerie globale"""
    # Vérifier que la trésorerie n'existe pas déjà avec le même nom dans la compagnie
    db_tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.nom == tresorerie.nom,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    if db_tresorerie:
        raise HTTPException(status_code=400, detail="Tresorerie with this name already exists")

    # Créer la trésorerie globale
    db_tresorerie = TresorerieModel(**tresorerie.dict(), compagnie_id=current_user.compagnie_id)
    db.add(db_tresorerie)
    db.commit()
    db.refresh(db_tresorerie)

    return db_tresorerie


def get_tresorerie_by_id(db: Session, current_user, tresorerie_id: uuid.UUID):
    """Récupère une trésorerie spécifique par son ID"""
    tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id,
        TresorerieModel.statut != "supprimé"  # Exclure les trésoreries supprimées
    ).first()

    if not tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")
    return tresorerie


def update_tresorerie(db: Session, current_user, tresorerie_id: uuid.UUID, tresorerie: schemas.TresorerieUpdate):
    """Met à jour une trésorerie existante"""
    db_tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id,
        TresorerieModel.statut != "supprimé"  # Exclure les trésoreries supprimées
    ).first()

    if not db_tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")

    update_data = tresorerie.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tresorerie, field, value)

    db.commit()
    db.refresh(db_tresorerie)
    return db_tresorerie


def delete_tresorerie(db: Session, current_user, tresorerie_id: uuid.UUID):
    """Supprime une trésorerie (en fait la met en statut supprimé)"""
    tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id,
        TresorerieModel.statut != "supprimé"  # Exclure les trésoreries supprimées
    ).first()

    if not tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")

    # Mise en statut "supprimé" pour conserver l'historique
    tresorerie.statut = "supprimé"
    db.commit()
    return {"message": "Tresorerie deleted successfully"}


def create_tresorerie_station(db: Session, current_user, tresorerie_station: schemas.TresorerieStationCreate):
    """Crée une trésorerie liée à une station"""
    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == tresorerie_station.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=403, detail="Station does not belong to your company")

    # Vérifier que la trésorerie existe
    tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_station.trésorerie_id
    ).first()

    if not tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")

    # Vérifier qu'elle n'existe pas déjà pour cette station
    existing = db.query(TresorerieStationModel).filter(
        TresorerieStationModel.trésorerie_id == tresorerie_station.trésorerie_id,
        TresorerieStationModel.station_id == tresorerie_station.station_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Trésorerie station already exists for this station")

    # Créer la trésorerie station
    db_tresorerie_station = TresorerieStationModel(**tresorerie_station.dict())
    db.add(db_tresorerie_station)
    db.commit()
    db.refresh(db_tresorerie_station)

    return db_tresorerie_station


def create_etat_initial_tresorerie(db: Session, current_user, etat_initial: schemas.EtatInitialTresorerieCreate):
    """Crée un état initial pour une trésorerie station"""
    # Vérifier que la trésorerie station appartient à l'utilisateur
    trésorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == etat_initial.tresorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not trésorerie_station:
        raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

    # Vérifier s'il existe déjà un état initial pour cette trésorerie station
    existing_etat = db.query(EtatInitialTresorerieModel).filter(
        EtatInitialTresorerieModel.tresorerie_station_id == etat_initial.tresorerie_station_id
    ).first()

    if existing_etat:
        raise HTTPException(status_code=400, detail="État initial already exists for this trésorerie station")

    # Créer l'état initial
    db_etat_initial = EtatInitialTresorerieModel(**etat_initial.dict())
    db.add(db_etat_initial)
    db.commit()
    db.refresh(db_etat_initial)

    # Mettre à jour le solde initial dans la trésorerie station
    trésorerie_station.solde_initial = etat_initial.montant
    trésorerie_station.solde_actuel = etat_initial.montant
    db.commit()

    return db_etat_initial


def create_mouvement_tresorerie(db: Session, current_user, mouvement: schemas.MouvementTresorerieCreate):
    """Crée un mouvement de trésorerie"""
    # Vérifier que la trésorerie station appartient à l'utilisateur
    trésorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == mouvement.trésorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not trésorerie_station:
        raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

    # Pour les sorties, vérifier qu'il y a suffisamment de fonds
    if mouvement.type_mouvement == "sortie":
        # Mettre à jour le solde pour être sûr de la valeur actuelle
        nouveau_solde = mettre_a_jour_solde_tresorerie(db, mouvement.trésorerie_station_id)

        if nouveau_solde < mouvement.montant:
            raise HTTPException(status_code=400, detail="Insufficient balance in trésorerie")

    # Créer le mouvement
    db_mouvement = MouvementTresorerieModel(**mouvement.dict())
    db.add(db_mouvement)
    db.commit()
    db.refresh(db_mouvement)

    # Mettre à jour le solde de la trésorerie
    mettre_a_jour_solde_tresorerie(db, mouvement.trésorerie_station_id)

    return db_mouvement


def get_mouvements_tresorerie(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les mouvements de trésorerie"""
    # Récupérer les mouvements pour les trésoreries station appartenant aux stations de l'utilisateur
    mouvements = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.trésorerie_station_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return mouvements


def create_transfert_tresorerie(db: Session, current_user, transfert: schemas.TransfertTresorerieCreate):
    """Crée un transfert entre trésoreries"""
    # Vérifier que les trésoreries station appartiennent à l'utilisateur
    source_trésorerie = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == transfert.trésorerie_source_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    destination_trésorerie = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == transfert.trésorerie_destination_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not source_trésorerie or not destination_trésorerie:
        raise HTTPException(status_code=403, detail="One or both trésoreries do not belong to your company")

    # Vérifier qu'on ne transfère pas à la même trésorerie
    if transfert.trésorerie_source_id == transfert.trésorerie_destination_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same trésorerie")

    # Vérifier qu'il y a suffisamment de fonds dans la source
    nouveau_solde_source = mettre_a_jour_solde_tresorerie(db, transfert.trésorerie_source_id)

    if nouveau_solde_source < transfert.montant:
        raise HTTPException(status_code=400, detail="Insufficient balance in source trésorerie")

    # Créer le transfert
    db_transfert = TransfertTresorerieModel(**transfert.dict())
    db.add(db_transfert)

    # Créer les mouvements dans les trésoreries concernées
    # Sortie de la source
    mouvement_sortie = MouvementTresorerieModel(
        trésorerie_station_id=transfert.trésorerie_source_id,
        type_mouvement="sortie",
        montant=transfert.montant,
        date_mouvement=transfert.date_transfert,
        description=f"Transfert vers trésorerie {transfert.trésorerie_destination_id}",
        module_origine="transfert",
        reference_origine=f"TRANS-{db_transfert.id}",
        utilisateur_id=transfert.utilisateur_id,
        numero_piece_comptable=transfert.numero_piece_comptable
    )
    db.add(mouvement_sortie)

    # Entrée dans la destination
    mouvement_entree = MouvementTresorerieModel(
        trésorerie_station_id=transfert.trésorerie_destination_id,
        type_mouvement="entrée",
        montant=transfert.montant,
        date_mouvement=transfert.date_transfert,
        description=f"Transfert depuis trésorerie {transfert.trésorerie_source_id}",
        module_origine="transfert",
        reference_origine=f"TRANS-{db_transfert.id}",
        utilisateur_id=transfert.utilisateur_id,
        numero_piece_comptable=transfert.numero_piece_comptable
    )
    db.add(mouvement_entree)

    db.commit()
    db.refresh(db_transfert)

    # Mettre à jour les soldes des trésoreries concernées
    mettre_a_jour_solde_tresorerie(db, transfert.trésorerie_source_id)
    mettre_a_jour_solde_tresorerie(db, transfert.trésorerie_destination_id)

    return db_transfert


def get_transferts_tresorerie(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les transferts de trésorerie"""
    # Récupérer les transferts pour les trésoreries station appartenant aux stations de l'utilisateur
    transferts = db.query(TransfertTresorerieModel).join(
        TresorerieStationModel,
        TransfertTresorerieModel.trésorerie_source_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return transferts