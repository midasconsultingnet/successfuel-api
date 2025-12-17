import re
import json
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
    # Jointure avec les tables Tresorerie et Station pour récupérer les données combinées
    query = db.query(TresorerieStationModel, TresorerieModel, Station).join(
        TresorerieModel,
        TresorerieStationModel.trésorerie_id == TresorerieModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    )

    results = query.offset(skip).limit(limit).all()

    # Préparer les résultats combinés et nettoyés
    processed_results = []
    for tresorerie_station, tresorerie, station in results:
        # Gérer la conversion du champ config s'il est au format JSON dans la base de données
        config_data = station.config
        if isinstance(config_data, str):
            try:
                config_data = json.loads(config_data)
            except json.JSONDecodeError:
                # Si ce n'est pas un JSON valide, laisser comme chaîne
                pass

        # Créer un dictionnaire combiné selon le schéma StationTresorerieResponse
        combined_result = {
            # Champs de Station
            'station_id': station.id,
            'compagnie_id': station.compagnie_id,
            'nom_station': station.nom,
            'code': station.code,
            'adresse': station.adresse,
            'coordonnees_gps': station.coordonnees_gps,
            'statut_station': station.statut,
            'config': config_data,

            # Champs de Tresorerie
            'trésorerie_id': tresorerie.id,
            'nom_tresorerie': tresorerie.nom,
            'type_tresorerie': tresorerie.type,
            'solde_initial_tresorerie': float(tresorerie.solde_initial),
            'devise': tresorerie.devise,
            'informations_bancaires': tresorerie.informations_bancaires,
            'statut_tresorerie': tresorerie.statut,

            # Champs de TresorerieStation
            'trésorerie_station_id': tresorerie_station.id,
            'solde_initial_station': float(tresorerie_station.solde_initial),
            'solde_actuel': float(tresorerie_station.solde_actuel),

            # Champs communs
            'created_at': station.created_at,
            'updated_at': station.updated_at
        }

        # Nettoyer les caractères spéciaux des résultats
        cleaned_result = clean_special_characters(combined_result)
        processed_results.append(cleaned_result)

    return processed_results


def clean_special_characters(data):
    """
    Fonction pour nettoyer les caractères spéciaux des données
    """
    if isinstance(data, dict):
        cleaned_dict = {}
        for key, value in data.items():
            # Nettoyer les caractères spéciaux dans les noms de clés pour des cas spécifiques (remplacer 'é' par 'e', etc.)
            clean_key = key
            if 'é' in key or 'è' in key or 'ê' in key or 'ë' in key or 'à' in key or 'á' in key or 'â' in key or 'ä' in key:
                clean_key = key.replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ë', 'e') \
                              .replace('É', 'E').replace('È', 'E').replace('Ê', 'E').replace('Ë', 'E') \
                              .replace('à', 'a').replace('á', 'a').replace('â', 'a').replace('ä', 'a') \
                              .replace('À', 'A').replace('Á', 'A').replace('Â', 'A').replace('Ä', 'A') \
                              .replace('ù', 'u').replace('ú', 'u').replace('û', 'u').replace('ü', 'u') \
                              .replace('Ù', 'U').replace('Ú', 'U').replace('Û', 'U').replace('Ü', 'U') \
                              .replace('î', 'i').replace('ï', 'i').replace('Î', 'I').replace('Ï', 'I') \
                              .replace('ô', 'o').replace('ö', 'o').replace('Ô', 'O').replace('Ö', 'O')

            cleaned_dict[clean_key] = clean_special_characters(value)
        return cleaned_dict
    elif isinstance(data, list):
        return [clean_special_characters(item) for item in data]
    elif isinstance(data, str):
        # Nettoyer les caractères spéciaux en conservant uniquement les lettres, chiffres, espaces et ponctuation standard
        cleaned = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)]', ' ', data)
        # Supprimer les espaces multiples
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    else:
        return data


def get_tresoreries_station_by_station(db: Session, current_user, station_id: uuid.UUID):
    """Récupère les trésoreries pour une station spécifique"""
    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=403, detail="Station does not belong to your company")

    # Récupérer les trésoreries de cette station spécifique avec jointure avec la table Tresorerie
    results = db.query(TresorerieStationModel, TresorerieModel).join(
        TresorerieModel,
        TresorerieStationModel.trésorerie_id == TresorerieModel.id
    ).filter(
        TresorerieStationModel.station_id == station_id
    ).all()

    # Préparer les résultats combinés et nettoyés
    processed_results = []
    for tresorerie_station, tresorerie in results:
        # Gérer la conversion du champ config s'il est au format JSON dans la base de données
        config_data = station.config
        if isinstance(config_data, str):
            try:
                config_data = json.loads(config_data)
            except json.JSONDecodeError:
                # Si ce n'est pas un JSON valide, laisser comme chaîne
                pass

        # Créer un dictionnaire combiné selon le schéma StationTresorerieResponse
        combined_result = {
            # Champs de Station
            'station_id': station.id,
            'compagnie_id': station.compagnie_id,
            'nom_station': station.nom,
            'code': station.code,
            'adresse': station.adresse,
            'coordonnees_gps': station.coordonnees_gps,
            'statut_station': station.statut,
            'config': config_data,

            # Champs de Tresorerie
            'trésorerie_id': tresorerie.id,
            'nom_tresorerie': tresorerie.nom,
            'type_tresorerie': tresorerie.type,
            'solde_initial_tresorerie': float(tresorerie.solde_initial),
            'devise': tresorerie.devise,
            'informations_bancaires': tresorerie.informations_bancaires,
            'statut_tresorerie': tresorerie.statut,

            # Champs de TresorerieStation
            'trésorerie_station_id': tresorerie_station.id,
            'solde_initial_station': float(tresorerie_station.solde_initial),
            'solde_actuel': float(tresorerie_station.solde_actuel),

            # Champs communs
            'created_at': station.created_at,
            'updated_at': station.updated_at
        }

        # Nettoyer les caractères spéciaux des résultats
        cleaned_result = clean_special_characters(combined_result)
        processed_results.append(cleaned_result)

    return processed_results


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
    # Nettoyer les données d'entrée avant de les appliquer
    cleaned_update_data = clean_special_characters(update_data)

    for field, value in cleaned_update_data.items():
        setattr(db_tresorerie, field, value)

    db.commit()
    db.refresh(db_tresorerie)

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(db_tresorerie.__dict__)
    return result


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

    # Dans ce cas, les données de sortie n'ont pas de chaînes à nettoyer,
    # mais pour une cohérence avec la fonction de nettoyage, on peut simplement retourner l'objet
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

    # Nettoyer les données d'entrée
    cleaned_data = clean_special_characters(etat_initial.dict())

    # Créer l'état initial
    db_etat_initial = EtatInitialTresorerieModel(**cleaned_data)
    db.add(db_etat_initial)
    db.commit()
    db.refresh(db_etat_initial)

    # Mettre à jour le solde initial dans la trésorerie station
    trésorerie_station.solde_initial = etat_initial.montant
    trésorerie_station.solde_actuel = etat_initial.montant
    db.commit()

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(db_etat_initial.__dict__)
    return result


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

    # Nettoyer les données d'entrée
    cleaned_data = clean_special_characters(mouvement.dict())

    # Créer le mouvement
    db_mouvement = MouvementTresorerieModel(**cleaned_data)
    db.add(db_mouvement)
    db.commit()
    db.refresh(db_mouvement)

    # Mettre à jour le solde de la trésorerie
    mettre_a_jour_solde_tresorerie(db, mouvement.trésorerie_station_id)

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(db_mouvement.__dict__)
    return result


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

    # Nettoyer les données d'entrée
    cleaned_data = clean_special_characters(transfert.dict())

    # Créer le transfert
    db_transfert = TransfertTresorerieModel(**cleaned_data)
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

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(db_transfert.__dict__)
    return result


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