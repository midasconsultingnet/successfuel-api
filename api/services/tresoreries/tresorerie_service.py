import re
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, text
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
from datetime import datetime, date


def mettre_a_jour_solde_tresorerie(db: Session, tresorerie_station_id: uuid.UUID):
    """Met à jour le solde actuel d'une trésorerie station en utilisant la vue matérialisée"""
    from sqlalchemy import text

    # Récupérer la trésorerie station
    tresorerie_station = db.query(TresorerieStationModel).filter(
        TresorerieStationModel.id == tresorerie_station_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=404, detail="Trésorerie station non trouvée")

    # Récupérer le solde calculé à partir de la nouvelle vue matérialisée
    try:
        result = db.execute(text("""
            SELECT solde_actuel
            FROM vue_solde_tresorerie_station
            WHERE tresorerie_station_id = :tresorerie_station_id
        """), {"tresorerie_station_id": tresorerie_station_id}).fetchone()

        if result:
            solde_actuel = float(result.solde_actuel)
        else:
            # Si aucun résultat, utiliser le solde initial
            solde_actuel = 0.0
    except Exception as e:
        # Si la vue n'existe pas, utiliser le solde initial
        logger.warning(f"Vue vue_solde_tresorerie_station non disponible: {e}")
        solde_actuel = 0.0

    # Mettre à jour le solde actuel dans la base
    # NOTE: Le champ solde_actuel a été supprimé de la table tresorerie_station
    # Donc on ne met plus à jour ce champ, mais on retourne le solde calculé
    return solde_actuel


def refresh_vue_solde_tresorerie(db: Session):
    """Rafraîchit les vues matérialisées des soldes de trésorerie"""
    from sqlalchemy import text

    try:
        db.execute(text("REFRESH MATERIALIZED VIEW vue_solde_tresorerie_globale"))
    except Exception as e:
        logger.warning(f"Impossible de rafraîchir la vue matérialisée vue_solde_tresorerie_globale: {e}")

    try:
        db.execute(text("REFRESH MATERIALIZED VIEW vue_solde_tresorerie_station"))
    except Exception as e:
        logger.warning(f"Impossible de rafraîchir la vue matérialisée vue_solde_tresorerie_station: {e}")

    db.commit()


def get_tresoreries_sans_methode_paiement(db: Session, current_user):
    """Récupère les tresoreries qui n'ont aucune méthode de paiement associée"""
    from sqlalchemy import text

    # Récupérer les IDs des trésoreries (globales et stations) qui ont des méthodes de paiement associées via la table de liaison
    tresoreries_avec_methode = db.execute(text("""
        SELECT DISTINCT tmp.tresorerie_id
        FROM tresorerie_methode_paiement tmp
        JOIN tresorerie t ON tmp.tresorerie_id = t.id
        LEFT JOIN tresorerie_station ts ON t.id = ts.tresorerie_id
        LEFT JOIN station s ON ts.station_id = s.id
        WHERE (t.compagnie_id = :compagnie_id OR s.compagnie_id = :compagnie_id)
        AND tmp.actif = true
    """), {"compagnie_id": current_user.compagnie_id}).fetchall()

    ids_avec_methode = [row.tresorerie_id for row in tresoreries_avec_methode]

    # Récupérer toutes les trésoreries (globales et stations) de la compagnie
    if not ids_avec_methode:
        # Si aucune trésorerie n'a de méthode de paiement associée, retourner toutes les trésoreries
        toutes_tresoreries = db.query(TresorerieModel).filter(
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).all()

        # Ajouter aussi les trésoreries stations liées à la compagnie
        toutes_tresoreries_station = db.query(TresorerieModel).join(
            TresorerieStationModel,
            TresorerieStationModel.tresorerie_id == TresorerieModel.id
        ).join(
            Station,
            TresorerieStationModel.station_id == Station.id
        ).filter(
            Station.compagnie_id == current_user.compagnie_id
        ).distinct(TresorerieModel.id).all()

        # Combiner les deux listes et supprimer les doublons
        toutes_tresoreries.extend([t for t in toutes_tresoreries_station if t not in toutes_tresoreries])

        return toutes_tresoreries
    else:
        # Récupérer les trésoreries globales sans méthodes de paiement
        tresoreries_globales_sans_methode = db.query(TresorerieModel).filter(
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).filter(
            ~TresorerieModel.id.in_(ids_avec_methode)
        ).all()

        # Récupérer les trésoreries stations sans méthodes de paiement
        tresoreries_stations_sans_methode = db.query(TresorerieModel).join(
            TresorerieStationModel,
            TresorerieStationModel.tresorerie_id == TresorerieModel.id
        ).join(
            Station,
            TresorerieStationModel.station_id == Station.id
        ).filter(
            Station.compagnie_id == current_user.compagnie_id
        ).filter(
            ~TresorerieModel.id.in_(ids_avec_methode)
        ).distinct(TresorerieModel.id).all()

        # Combiner les deux listes et supprimer les doublons
        resultat = tresoreries_globales_sans_methode
        resultat.extend([t for t in tresoreries_stations_sans_methode if t not in resultat])

        return resultat


def get_mouvements_tresorerie_by_reference(db: Session, current_user, reference: str):
    """Récupère les mouvements de trésorerie par référence d'origine"""
    # Récupérer les mouvements de trésorerie avec la référence spécifiée
    # On joint avec les tables appropriées pour vérifier que l'utilisateur a accès aux données
    mouvements = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id,
        isouter=True  # LEFT JOIN pour inclure les mouvements liés directement aux trésoreries globales
    ).join(
        TresorerieModel,
        (
            (MouvementTresorerieModel.tresorerie_globale_id == TresorerieModel.id) |
            (TresorerieStationModel.tresorerie_id == TresorerieModel.id)
        )
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id,
        isouter=True  # LEFT JOIN pour inclure les trésoreries globales non liées à une station
    ).filter(
        MouvementTresorerieModel.reference_origine == reference
    ).filter(
        (
            (TresorerieModel.compagnie_id == current_user.compagnie_id) |
            (Station.compagnie_id == current_user.compagnie_id)
        )
    ).all()

    return mouvements


def get_tresoreries_station(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les tresoreries station appartenant aux stations de l'utilisateur"""
    # Jointure avec les tables Tresorerie et Station pour récupérer les données combinées
    query = db.query(TresorerieStationModel, TresorerieModel, Station).join(
        TresorerieModel,
        TresorerieStationModel.tresorerie_id == TresorerieModel.id
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

        # Récupérer le solde de la trésorerie globale à partir de la vue matérialisée
        try:
            solde_tresorerie_globale_result = db.execute(text("""
                SELECT solde_tresorerie
                FROM vue_solde_tresorerie_globale
                WHERE tresorerie_id = :tresorerie_id
            """), {"tresorerie_id": tresorerie.id}).fetchone()

            solde_tresorerie_globale = float(solde_tresorerie_globale_result.solde_tresorerie) if solde_tresorerie_globale_result else float(tresorerie.solde_initial or 0)
        except Exception as e:
            # Si la vue n'existe pas, utiliser le solde initial
            logger.warning(f"Vue vue_solde_tresorerie_globale non disponible: {e}")
            solde_tresorerie_globale = float(tresorerie.solde_initial or 0)

        # Récupérer le solde de la trésorerie pour cette station spécifique
        try:
            solde_tresorerie_station_result = db.execute(text("""
                SELECT solde_actuel
                FROM vue_solde_tresorerie_station
                WHERE tresorerie_station_id = :tresorerie_station_id
            """), {"tresorerie_station_id": tresorerie_station.id}).fetchone()
        except Exception as e:
            # Si la vue n'existe pas, utiliser le solde initial
            logger.warning(f"Vue vue_solde_tresorerie_station non disponible: {e}")
            solde_tresorerie_station_result = None

        solde_tresorerie_station = float(solde_tresorerie_station_result.solde_actuel) if solde_tresorerie_station_result else 0.0

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
            'tresorerie_id': tresorerie.id,
            'nom_tresorerie': tresorerie.nom,
            'type_tresorerie': tresorerie.type,
            'solde_initial_tresorerie': float(tresorerie.solde_initial),
            'solde_tresorerie': solde_tresorerie_globale,  # Solde global de la trésorerie
            'devise': tresorerie.devise,
            'informations_bancaires': tresorerie.informations_bancaires,
            'statut_tresorerie': tresorerie.statut,

            # Champs de TresorerieStation
            'tresorerie_station_id': tresorerie_station.id,
            'solde_initial_station': 0.0,  # Le champ solde_initial a été supprimé de tresorerie_station
            'solde_actuel_station': solde_tresorerie_station,  # Solde de la trésorerie pour cette station spécifique

            # Champs communs
            'created_at': station.created_at,
            'updated_at': station.updated_at
        }

        # Ajouter le résultat combiné (sans nettoyage pour préserver les types de données)
        processed_results.append(combined_result)

    return processed_results


# CRUD pour TresorerieStation
def get_tresorerie_station_by_id(db: Session, current_user, tresorerie_station_id: uuid.UUID):
    """Récupère une association trésorerie-station spécifique par son ID"""
    tresorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == tresorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=404, detail="Tresorerie station not found")

    return tresorerie_station


def update_tresorerie_station(db: Session, current_user, tresorerie_station_id: uuid.UUID, tresorerie_station_update: schemas.TresorerieStationUpdate):
    """Met à jour une association trésorerie-station existante"""
    tresorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == tresorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=404, detail="Tresorerie station not found")

    update_data = tresorerie_station_update.dict(exclude_unset=True)
    # Nettoyer les données d'entrée avant de les appliquer
    cleaned_update_data = clean_special_characters(update_data)

    for field, value in cleaned_update_data.items():
        setattr(tresorerie_station, field, value)

    db.commit()
    db.refresh(tresorerie_station)

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(tresorerie_station.__dict__)
    return result


def delete_tresorerie_station(db: Session, current_user, tresorerie_station_id: uuid.UUID):
    """Supprime une association trésorerie-station"""
    tresorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == tresorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=404, detail="Tresorerie station not found")

    # Supprimer la relation
    db.delete(tresorerie_station)
    db.commit()
    return {"message": "Tresorerie station deleted successfully"}


# CRUD pour MouvementTresorerie
def get_mouvements_tresorerie(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère tous les mouvements de trésorerie appartenant à la compagnie de l'utilisateur"""
    mouvements = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return mouvements


def get_mouvement_tresorerie_by_id(db: Session, current_user, mouvement_id: uuid.UUID):
    """Récupère un mouvement de trésorerie spécifique par son ID"""
    mouvement = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        MouvementTresorerieModel.id == mouvement_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not mouvement:
        raise HTTPException(status_code=404, detail="Mouvement trésorerie not found")

    return mouvement


def update_mouvement_tresorerie(db: Session, current_user, mouvement_id: uuid.UUID, mouvement_update: schemas.MouvementTresorerieUpdate):
    """Met à jour un mouvement de trésorerie existant"""
    mouvement = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        MouvementTresorerieModel.id == mouvement_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not mouvement:
        raise HTTPException(status_code=404, detail="Mouvement trésorerie not found")

    # Sauvegarder les anciennes valeurs pour vérifier si le type ou le montant change
    ancien_type_mouvement = mouvement.type_mouvement
    ancien_montant = mouvement.montant

    update_data = mouvement_update.dict(exclude_unset=True)
    # Nettoyer les données d'entrée avant de les appliquer
    cleaned_update_data = clean_special_characters(update_data)

    for field, value in cleaned_update_data.items():
        setattr(mouvement, field, value)

    db.commit()
    db.refresh(mouvement)

    # Dans la nouvelle architecture, les soldes sont gérés automatiquement par les triggers
    # On n'a plus besoin de rafraîchir les vues matérialisées ici

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(mouvement.__dict__)
    return result


def annuler_mouvement_tresorerie(db: Session, current_user, mouvement_id: uuid.UUID):
    """Annule un mouvement de trésorerie en utilisant la fonction PostgreSQL"""
    from sqlalchemy import text

    # Récupérer le mouvement à annuler
    mouvement = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        MouvementTresorerieModel.id == mouvement_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not mouvement:
        raise HTTPException(status_code=404, detail="Mouvement trésorerie not found")

    # Vérifier si le mouvement est déjà annulé
    if mouvement.est_annule:
        raise HTTPException(status_code=400, detail="Le mouvement est déjà annulé")

    # Appeler la fonction PostgreSQL pour annuler le mouvement
    result = db.execute(text("SELECT annuler_mouvement_tresorerie(:mvt_id, :user_id)"),
                        {"mvt_id": mouvement_id, "user_id": current_user.id}).fetchone()

    if not result:
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation du mouvement")

    # Rafraîchir l'objet mouvement pour refléter les changements
    db.refresh(mouvement)

    return {"message": "Mouvement trésorerie annulé avec succès", "mouvement_inverse_id": result[0]}


def delete_mouvement_tresorerie(db: Session, current_user, mouvement_id: uuid.UUID):
    """Supprime un mouvement de trésorerie"""
    mouvement = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        MouvementTresorerieModel.id == mouvement_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not mouvement:
        raise HTTPException(status_code=404, detail="Mouvement trésorerie not found")

    # Supprimer le mouvement
    db.delete(mouvement)
    db.commit()
    return {"message": "Mouvement trésorerie deleted successfully"}


# CRUD pour TransfertTresorerie
def get_transferts_tresorerie(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère tous les transferts de trésorerie appartenant à la compagnie de l'utilisateur"""
    from sqlalchemy.orm import aliased

    # Créer des alias pour les tables de trésorerie
    TresorerieSource = aliased(TresorerieModel)
    TresorerieDestination = aliased(TresorerieModel)

    # Faire une requête qui joint les trésoreries source et destination pour récupérer leurs noms
    transferts = db.query(
        TransfertTresorerieModel,
        TresorerieSource.nom.label('nom_tresorerie_source'),
        TresorerieDestination.nom.label('nom_tresorerie_destination')
    ).join(
        TresorerieSource,
        TransfertTresorerieModel.tresorerie_source_id == TresorerieSource.id
    ).join(
        TresorerieDestination,
        TransfertTresorerieModel.tresorerie_destination_id == TresorerieDestination.id
    ).filter(
        TresorerieSource.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    # Convertir les résultats en objets TransfertTresorerie avec les noms des trésoreries
    result = []
    for transfert_row in transferts:
        transfert = transfert_row[0]  # L'objet TransfertTresorerieModel
        nom_source = transfert_row[1]  # nom_tresorerie_source
        nom_destination = transfert_row[2]  # nom_tresorerie_destination

        # Ajouter les noms des trésoreries à l'objet transfert
        transfert.nom_tresorerie_source = nom_source
        transfert.nom_tresorerie_destination = nom_destination

        result.append(transfert)

    return result


def get_transfert_tresorerie_by_id(db: Session, current_user, transfert_id: uuid.UUID):
    """Récupère un transfert de trésorerie spécifique par son ID"""
    from sqlalchemy.orm import aliased

    # Créer des alias pour les tables de trésorerie
    TresorerieSource = aliased(TresorerieModel)
    TresorerieDestination = aliased(TresorerieModel)

    transfert_row = db.query(
        TransfertTresorerieModel,
        TresorerieSource.nom.label('nom_tresorerie_source'),
        TresorerieDestination.nom.label('nom_tresorerie_destination')
    ).join(
        TresorerieSource,
        TransfertTresorerieModel.tresorerie_source_id == TresorerieSource.id
    ).join(
        TresorerieDestination,
        TransfertTresorerieModel.tresorerie_destination_id == TresorerieDestination.id
    ).filter(
        TransfertTresorerieModel.id == transfert_id,
        TresorerieSource.compagnie_id == current_user.compagnie_id
    ).first()

    if not transfert_row:
        raise HTTPException(status_code=404, detail="Transfert trésorerie not found")

    transfert = transfert_row[0]  # L'objet TransfertTresorerieModel
    nom_source = transfert_row[1]  # nom_tresorerie_source
    nom_destination = transfert_row[2]  # nom_tresorerie_destination

    # Ajouter les noms des trésoreries à l'objet transfert
    transfert.nom_tresorerie_source = nom_source
    transfert.nom_tresorerie_destination = nom_destination

    return transfert


def update_transfert_tresorerie(db: Session, current_user, transfert_id: uuid.UUID, transfert_update: schemas.TransfertTresorerieUpdate):
    """Met à jour un transfert de trésorerie existant"""
    transfert = db.query(TransfertTresorerieModel).join(
        TresorerieModel,
        TransfertTresorerieModel.tresorerie_source_id == TresorerieModel.id
    ).filter(
        TransfertTresorerieModel.id == transfert_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not transfert:
        raise HTTPException(status_code=404, detail="Transfert trésorerie not found")

    update_data = transfert_update.dict(exclude_unset=True)
    # Nettoyer les données d'entrée avant de les appliquer
    cleaned_update_data = clean_special_characters(update_data)

    for field, value in cleaned_update_data.items():
        setattr(transfert, field, value)

    db.commit()
    db.refresh(transfert)

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(transfert.__dict__)
    return result


def delete_transfert_tresorerie(db: Session, current_user, transfert_id: uuid.UUID):
    """Supprime un transfert de trésorerie"""
    transfert = db.query(TransfertTresorerieModel).join(
        TresorerieModel,
        TransfertTresorerieModel.tresorerie_source_id == TresorerieModel.id
    ).filter(
        TransfertTresorerieModel.id == transfert_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not transfert:
        raise HTTPException(status_code=404, detail="Transfert trésorerie not found")

    # Supprimer le transfert
    db.delete(transfert)
    db.commit()
    return {"message": "Transfert trésorerie deleted successfully"}


# Endpoints spécifiques pour la nouvelle architecture
def get_solde_tresorerie_station(db: Session, current_user, tresorerie_station_id: uuid.UUID):
    """Récupère le solde d'une trésorerie pour une station spécifique"""
    # Vérifier que la trésorerie station appartient à l'utilisateur
    tresorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == tresorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=404, detail="Tresorerie station not found")

    # Utiliser la fonction existante pour mettre à jour et récupérer le solde
    return mettre_a_jour_solde_tresorerie(db, tresorerie_station_id)


def get_solde_tresorerie_globale(db: Session, current_user, tresorerie_id: uuid.UUID):
    """Récupère le solde d'une trésorerie globale"""
    from sqlalchemy import text

    # Vérifier que la trésorerie appartient à l'utilisateur
    tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie globale non trouvée")

    # Récupérer le solde calculé à partir de la vue matérialisée
    try:
        result = db.execute(text("""
            SELECT solde_tresorerie
            FROM vue_solde_tresorerie_globale
            WHERE tresorerie_id = :tresorerie_id
        """), {"tresorerie_id": tresorerie_id}).fetchone()

        if result:
            solde_actuel = float(result.solde_tresorerie)
        else:
            # Si aucun résultat, utiliser le solde initial
            solde_actuel = float(tresorerie.solde_initial or 0.0)
    except Exception as e:
        # Si la vue n'existe pas, utiliser le solde initial
        logger.warning(f"Vue vue_solde_tresorerie_globale non disponible: {e}")
        solde_actuel = float(tresorerie.solde_initial or 0.0)

    return solde_actuel


def cloture_soldes_mensuels(db: Session, mois: date):
    """Effectue la clôture des soldes mensuels en appelant le service de clôture"""
    # Importer la fonction depuis le module de clôture
    from .cloture_service import cloturer_soldes_mensuels as cloture_mensuelle
    return cloture_mensuelle(db, mois)


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
    """Récupère les tresoreries pour une station spécifique"""
    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=403, detail="Station does not belong to your company")

    # Récupérer les tresoreries de cette station spécifique avec jointure avec la table Tresorerie
    results = db.query(TresorerieStationModel, TresorerieModel).join(
        TresorerieModel,
        TresorerieStationModel.tresorerie_id == TresorerieModel.id
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

        # Récupérer le solde de la trésorerie globale à partir de la vue matérialisée
        try:
            solde_tresorerie_globale_result = db.execute(text("""
                SELECT solde_tresorerie
                FROM vue_solde_tresorerie_globale
                WHERE tresorerie_id = :tresorerie_id
            """), {"tresorerie_id": tresorerie.id}).fetchone()

            solde_tresorerie_globale = float(solde_tresorerie_globale_result.solde_tresorerie) if solde_tresorerie_globale_result else float(tresorerie.solde_initial or 0)
        except Exception as e:
            # Si la vue n'existe pas, utiliser le solde initial
            logger.warning(f"Vue vue_solde_tresorerie_globale non disponible: {e}")
            solde_tresorerie_globale = float(tresorerie.solde_initial or 0)

        # Récupérer le solde de la trésorerie pour cette station spécifique
        try:
            solde_tresorerie_station_result = db.execute(text("""
                SELECT solde_actuel
                FROM vue_solde_tresorerie_station
                WHERE tresorerie_station_id = :tresorerie_station_id
            """), {"tresorerie_station_id": tresorerie_station.id}).fetchone()
        except Exception as e:
            # Si la vue n'existe pas, utiliser le solde initial
            logger.warning(f"Vue vue_solde_tresorerie_station non disponible: {e}")
            solde_tresorerie_station_result = None

        solde_tresorerie_station = float(solde_tresorerie_station_result.solde_actuel) if solde_tresorerie_station_result else 0.0

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
            'tresorerie_id': tresorerie.id,
            'nom_tresorerie': tresorerie.nom,
            'type_tresorerie': tresorerie.type,
            'solde_initial_tresorerie': float(tresorerie.solde_initial),
            'solde_tresorerie': solde_tresorerie_globale,  # Solde global de la trésorerie
            'devise': tresorerie.devise,
            'informations_bancaires': tresorerie.informations_bancaires,
            'statut_tresorerie': tresorerie.statut,

            # Champs de TresorerieStation
            'tresorerie_station_id': tresorerie_station.id,
            'solde_initial_station': 0.0,  # Le champ solde_initial a été supprimé de tresorerie_station
            'solde_actuel_station': solde_tresorerie_station,  # Solde de la trésorerie pour cette station spécifique

            # Champs communs
            'created_at': station.created_at,
            'updated_at': station.updated_at
        }

        # Ajouter le résultat combiné (sans nettoyage pour préserver les types de données)
        processed_results.append(combined_result)

    return processed_results


def get_tresoreries(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les tresoreries appartenant à la compagnie de l'utilisateur"""
    tresoreries = db.query(TresorerieModel).filter(
        TresorerieModel.compagnie_id == current_user.compagnie_id,
        TresorerieModel.statut != "supprimé"  # Exclure les tresoreries supprimées
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

    # Créer la trésorerie globale sans modifier directement le solde_tresorerie
    db_tresorerie = TresorerieModel(
        nom=tresorerie.nom,
        type=tresorerie.type,
        solde_initial=tresorerie.solde_initial,
        solde_tresorerie=0,  # Initialiser à 0, le solde sera calculé à partir des mouvements
        devise=tresorerie.devise,
        informations_bancaires=tresorerie.informations_bancaires,
        statut=tresorerie.statut,
        compagnie_id=current_user.compagnie_id
    )

    db.add(db_tresorerie)
    db.commit()
    db.refresh(db_tresorerie)

    # Si un solde_initial est spécifié, créer un mouvement initial pour la trésorerie globale
    if tresorerie.solde_initial and tresorerie.solde_initial > 0:
        # Pour une trésorerie globale, nous devons créer un mouvement de type global
        # lié directement à la trésorerie via tresorerie_globale_id
        # Créer un mouvement d'entrée global pour initialiser le solde
        from ..tresorerie.mouvement_manager import MouvementTresorerieManager
        MouvementTresorerieManager.creer_mouvement_general(
            db=db,
            type_mouvement="entrée",
            montant=float(tresorerie.solde_initial),
            utilisateur_id=current_user.id,
            description=f"Initialisation du solde de la trésorerie '{tresorerie.nom}'",
            module_origine="tresorerie",
            reference_origine=f"INIT-{db_tresorerie.id}",
            tresorerie_globale_id=db_tresorerie.id  # Lier le mouvement directement à la trésorerie
        )

    return db_tresorerie


def get_tresorerie_by_id(db: Session, current_user, tresorerie_id: uuid.UUID):
    """Récupère une trésorerie spécifique par son ID"""
    tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id,
        TresorerieModel.statut != "supprimé"  # Exclure les tresoreries supprimées
    ).first()

    if not tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")
    return tresorerie


def update_tresorerie(db: Session, current_user, tresorerie_id: uuid.UUID, tresorerie: schemas.TresorerieUpdate):
    """Met à jour une trésorerie existante"""
    db_tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id,
        TresorerieModel.statut != "supprimé"  # Exclure les tresoreries supprimées
    ).first()

    if not db_tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")

    update_data = tresorerie.dict(exclude_unset=True)
    # Nettoyer les données d'entrée avant de les appliquer
    cleaned_update_data = clean_special_characters(update_data)

    # Vérifier si le solde_initial est inclus dans la mise à jour
    ancien_solde_initial = db_tresorerie.solde_initial
    nouveau_solde_initial = cleaned_update_data.get('solde_initial', None)

    for field, value in cleaned_update_data.items():
        setattr(db_tresorerie, field, value)

    # Si le solde_initial a été modifié, créer les mouvements pour refléter le changement
    if nouveau_solde_initial is not None and nouveau_solde_initial != ancien_solde_initial:
        # Trouver l'ancien mouvement d'initialisation s'il existe
        from ...models.tresorerie import MouvementTresorerie as MouvementTresorerieModel
        ancien_mouvement = db.query(MouvementTresorerieModel).filter(
            MouvementTresorerieModel.reference_origine == f"INIT-{tresorerie_id}",
            MouvementTresorerieModel.tresorerie_globale_id == tresorerie_id
        ).first()

        if ancien_mouvement:
            # Créer un mouvement d'annulation pour annuler l'ancien solde initial
            from ..tresorerie.mouvement_manager import MouvementTresorerieManager
            MouvementTresorerieManager.creer_mouvement_general(
                db=db,
                type_mouvement="sortie",  # Inverse de l'entrée initiale
                montant=float(ancien_solde_initial) if ancien_solde_initial else 0,
                utilisateur_id=current_user.id,
                description=f"Annulation du solde initial précédent pour la trésorerie '{db_tresorerie.nom}'",
                module_origine="tresorerie",
                reference_origine=f"ANNULE-INIT-{tresorerie_id}",
                tresorerie_globale_id=db_tresorerie.id
            )

        # Créer un nouveau mouvement pour le nouveau solde initial
        if nouveau_solde_initial and nouveau_solde_initial > 0:
            from ..tresorerie.mouvement_manager import MouvementTresorerieManager
            MouvementTresorerieManager.creer_mouvement_general(
                db=db,
                type_mouvement="entrée",
                montant=float(nouveau_solde_initial),
                utilisateur_id=current_user.id,
                description=f"Nouveau solde initial pour la trésorerie '{db_tresorerie.nom}'",
                module_origine="tresorerie",
                reference_origine=f"INIT-{tresorerie_id}",
                tresorerie_globale_id=db_tresorerie.id
            )

    db.commit()
    db.refresh(db_tresorerie)

    return db_tresorerie


def delete_tresorerie(db: Session, current_user, tresorerie_id: uuid.UUID):
    """Supprime une trésorerie"""
    # Vérifier que la trésorerie appartient à l'utilisateur
    db_tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")

    # Vérifier s'il y a des mouvements associés à cette trésorerie
    # Soit directement via la table mouvement_tresorerie, soit via les associations trésorerie-station
    from sqlalchemy import text

    # Compter les mouvements associés à cette trésorerie
    result = db.execute(text("""
        SELECT COUNT(*) as count
        FROM mouvement_tresorerie mt
        JOIN tresorerie_station ts ON mt.tresorerie_station_id = ts.id
        WHERE ts.tresorerie_id = :tresorerie_id
    """), {"tresorerie_id": tresorerie_id}).fetchone()

    mouvement_count = result.count

    # Compter les associations trésorerie-station
    association_count = db.query(TresorerieStationModel).filter(
        TresorerieStationModel.tresorerie_id == tresorerie_id
    ).count()

    # Si la trésorerie a des mouvements ou des associations, ne pas la supprimer complètement
    if mouvement_count > 0 or association_count > 0:
        # Marquer la trésorerie comme supprimée
        db_tresorerie.statut = "supprimé"
        db.commit()
        db.refresh(db_tresorerie)
        return {"message": "Trésorerie marquée comme supprimée (a des mouvements ou associations)"}
    else:
        # Supprimer complètement la trésorerie
        db.delete(db_tresorerie)
        db.commit()
        return {"message": "Trésorerie supprimée complètement de la base de données"}


def create_tresorerie_station(db: Session, current_user, tresorerie_station: schemas.TresorerieStationCreate):
    """Crée une association trésorerie-station"""
    # Vérifier que la trésorerie appartient à la même compagnie que la station
    tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_station.tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    station = db.query(Station).filter(
        Station.id == tresorerie_station.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie or not station:
        raise HTTPException(status_code=403, detail="Trésorerie or station does not belong to your company")

    # Vérifier que l'association n'existe pas déjà
    existing_association = db.query(TresorerieStationModel).filter(
        TresorerieStationModel.tresorerie_id == tresorerie_station.tresorerie_id,
        TresorerieStationModel.station_id == tresorerie_station.station_id
    ).first()

    if existing_association:
        raise HTTPException(status_code=400, detail="Association trésorerie-station already exists")

    # Créer l'association
    db_tresorerie_station = TresorerieStationModel(
        tresorerie_id=tresorerie_station.tresorerie_id,
        station_id=tresorerie_station.station_id
    )
    db.add(db_tresorerie_station)
    db.commit()
    db.refresh(db_tresorerie_station)

    return db_tresorerie_station


def create_etat_initial_tresorerie(db: Session, current_user, etat_initial: schemas.EtatInitialTresorerieCreate):
    """Crée un état initial de trésorerie avec rafraîchissement de la vue matérialisée"""
    from sqlalchemy import text

    # Vérifier que la trésorerie station appartient à l'utilisateur
    tresorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == etat_initial.tresorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

    # Nettoyer les données d'entrée
    cleaned_data = clean_special_characters(etat_initial.dict())

    # Remplacer enregistre_par par l'utilisateur connecté s'il est différent
    if cleaned_data['enregistre_par'] != current_user.id:
        cleaned_data['enregistre_par'] = current_user.id

    # Créer l'état initial
    db_etat_initial = EtatInitialTresorerieModel(**cleaned_data)
    db.add(db_etat_initial)
    db.commit()
    db.refresh(db_etat_initial)

    # Rafraîchir la vue matérialisée pour les soldes
    refresh_vue_solde_tresorerie(db)

    # Nettoyer les données de sortie avant de les retourner
    result = clean_special_characters(db_etat_initial.__dict__)
    return result


def create_mouvement_tresorerie(db: Session, current_user, mouvement: schemas.MouvementTresorerieCreate):
    """Crée un mouvement de trésorerie"""
    from sqlalchemy import text

    # Vérifier que la trésorerie station appartient à l'utilisateur
    tresorerie_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == mouvement.tresorerie_station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=403, detail="Trésorerie station does not belong to your company")

    # Nettoyer les données d'entrée
    cleaned_data = clean_special_characters(mouvement.dict())

    # Remplacer l'utilisateur_id par l'utilisateur connecté s'il n'est pas fourni ou s'il est différent
    if not cleaned_data.get('utilisateur_id'):
        cleaned_data['utilisateur_id'] = current_user.id
    elif cleaned_data['utilisateur_id'] != current_user.id:
        # Si un utilisateur_id est fourni mais différent de l'utilisateur connecté,
        # on remplace par l'utilisateur connecté pour des raisons de sécurité
        cleaned_data['utilisateur_id'] = current_user.id

    # Créer le mouvement en utilisant le manager centralisé
    from ..tresorerie.mouvement_manager import MouvementTresorerieManager
    db_mouvement = MouvementTresorerieManager.creer_mouvement_general(
        db,
        type_mouvement=mouvement.type_mouvement,
        montant=mouvement.montant,
        utilisateur_id=current_user.id,
        description=mouvement.description,
        module_origine=mouvement.module_origine,
        reference_origine=mouvement.reference_origine,
        tresorerie_station_id=mouvement.tresorerie_station_id,
        commentaire=mouvement.commentaire,
        statut=mouvement.statut
    )

    # Retourner l'objet SQLAlchemy directement au lieu du dictionnaire nettoyé
    # Cela permet à FastAPI de convertir correctement en objet Pydantic
    return db_mouvement


def get_mouvements_tresorerie(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Récupère les mouvements de trésorerie"""
    # Récupérer les mouvements pour les tresoreries station appartenant aux stations de l'utilisateur
    mouvements = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return mouvements


def get_mouvements_tresorerie_by_id(db: Session, current_user, tresorerie_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Récupère les mouvements d'une trésorerie spécifique avec pagination"""
    # Récupérer les mouvements pour une trésorerie spécifique appartenant à l'utilisateur
    # Cela inclut les mouvements liés directement à la trésorerie (via tresorerie_globale_id)
    # et les mouvements liés via la liaison trésorerie-station

    # Requête pour les mouvements liés directement à la trésorerie
    mouvements_directs = db.query(MouvementTresorerieModel).join(
        TresorerieModel,
        MouvementTresorerieModel.tresorerie_globale_id == TresorerieModel.id
    ).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    )

    # Requête pour les mouvements liés via la liaison trésorerie-station
    mouvements_via_station = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id
    ).join(
        TresorerieModel,
        TresorerieStationModel.tresorerie_id == TresorerieModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    )

    # Combiner les deux requêtes avec UNION
    tous_mouvements = mouvements_directs.union(mouvements_via_station)

    # Appliquer pagination et retourner
    mouvements = tous_mouvements.offset(skip).limit(limit).all()

    return mouvements


def create_transfert_tresorerie(db: Session, current_user, transfert: schemas.TransfertTresorerieCreate):
    """Crée un transfert de trésorerie"""
    from sqlalchemy import text

    logging.info(f"Création d'un transfert de trésorerie: {transfert}")
    logging.info(f"ID trésorerie source: {transfert.tresorerie_source_id}")
    logging.info(f"ID trésorerie destination: {transfert.tresorerie_destination_id}")
    logging.info(f"Montant du transfert: {transfert.montant}")

    # Vérifier que les trésoreries source et destination appartiennent à la même compagnie que l'utilisateur
    # On vérifie d'abord si les IDs correspondent à des trésoreries station
    logging.info("Vérification des trésoreries station...")
    tresorerie_source_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == transfert.tresorerie_source_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    tresorerie_destination_station = db.query(TresorerieStationModel).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TresorerieStationModel.id == transfert.tresorerie_destination_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    logging.info(f"Trésorerie source station trouvée: {tresorerie_source_station is not None}")
    logging.info(f"Trésorerie destination station trouvée: {tresorerie_destination_station is not None}")

    # Si les IDs ne correspondent pas à des trésoreries station, vérifier s'ils correspondent à des trésoreries globales
    tresorerie_source_globale = None
    tresorerie_destination_globale = None

    if not tresorerie_source_station:
        logging.info("Recherche de la trésorerie source globale...")
        tresorerie_source_globale = db.query(TresorerieModel).filter(
            TresorerieModel.id == transfert.tresorerie_source_id,
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).first()
        logging.info(f"Trésorerie source globale trouvée: {tresorerie_source_globale is not None}")

    if not tresorerie_destination_station:
        logging.info("Recherche de la trésorerie destination globale...")
        tresorerie_destination_globale = db.query(TresorerieModel).filter(
            TresorerieModel.id == transfert.tresorerie_destination_id,
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).first()
        logging.info(f"Trésorerie destination globale trouvée: {tresorerie_destination_globale is not None}")

    # Vérifier que les deux trésoreries existent et appartiennent à la même compagnie
    if not (tresorerie_source_station or tresorerie_source_globale) or not (tresorerie_destination_station or tresorerie_destination_globale):
        logging.error("Erreur: Trésorerie source ou destination n'appartient pas à la compagnie de l'utilisateur")
        raise HTTPException(status_code=403, detail="Trésorerie source or destination does not belong to your company")

    logging.info("Vérification de la disponibilité des fonds dans la trésorerie source...")
    # Vérifier qu'il y a suffisamment de fonds dans la trésorerie source
    # Pour les trésoreries station, on utilise la vue de solde
    if tresorerie_source_station:
        logging.info("Calcul du solde pour la trésorerie station source...")
        result = db.execute(text("""
            SELECT solde_actuel
            FROM vue_solde_tresorerie_station
            WHERE tresorerie_station_id = :tresorerie_station_id
        """), {"tresorerie_station_id": transfert.tresorerie_source_id}).fetchone()
        solde_actuel = float(result.solde_actuel) if result else 0.0
        logging.info(f"Solde actuel de la trésorerie station source: {solde_actuel}")
    else:
        logging.info("Calcul du solde pour la trésorerie globale source...")
        # Pour les trésoreries globales, on calcule le solde à partir des mouvements
        from sqlalchemy import func, case
        result = db.query(
            func.coalesce(func.sum(
                case(
                    (MouvementTresorerieModel.type_mouvement == 'entrée', MouvementTresorerieModel.montant),
                    (MouvementTresorerieModel.type_mouvement == 'sortie', -MouvementTresorerieModel.montant),
                    else_=0
                )
            ), 0).label('solde')
        ).filter(
            MouvementTresorerieModel.tresorerie_globale_id == transfert.tresorerie_source_id,
            MouvementTresorerieModel.statut == 'validé'
        ).first()

        solde_actuel = float(result.solde) if result else 0.0
        logging.info(f"Solde calculé de la trésorerie globale source: {solde_actuel}")

    if solde_actuel < transfert.montant:
        logging.error(f"Solde insuffisant: disponible={solde_actuel}, demandé={transfert.montant}")
        raise HTTPException(status_code=400, detail="Insufficient balance in source trésorerie")

    logging.info("Création de l'enregistrement de transfert...")
    # Nettoyer les données d'entrée
    cleaned_data = clean_special_characters(transfert.dict())

    # Toujours remplacer utilisateur_id par l'utilisateur connecté, même s'il est fourni dans le payload
    cleaned_data['utilisateur_id'] = current_user.id

    # Créer le transfert
    db_transfert = TransfertTresorerieModel(**cleaned_data)
    db.add(db_transfert)
    db.commit()
    db.refresh(db_transfert)
    logging.info(f"Transfert créé avec succès, ID: {db_transfert.id}")

    # Créer les mouvements correspondants en utilisant le manager centralisé
    logging.info("Création des mouvements de trésorerie...")
    from ..tresorerie.mouvement_manager import MouvementTresorerieManager

    # Déterminer les paramètres pour les mouvements en fonction du type de trésorerie
    # Pour les trésoreries station
    if tresorerie_source_station:
        logging.info("Paramètres pour mouvement source: trésorerie station")
        source_params = {"tresorerie_station_id": transfert.tresorerie_source_id}
    else:
        logging.info("Paramètres pour mouvement source: trésorerie globale")
        # Pour les trésoreries globales
        source_params = {"tresorerie_globale_id": transfert.tresorerie_source_id}

    if tresorerie_destination_station:
        logging.info("Paramètres pour mouvement destination: trésorerie station")
        destination_params = {"tresorerie_station_id": transfert.tresorerie_destination_id}
    else:
        logging.info("Paramètres pour mouvement destination: trésorerie globale")
        # Pour les trésoreries globales
        destination_params = {"tresorerie_globale_id": transfert.tresorerie_destination_id}

    logging.info("Création du mouvement de sortie pour la trésorerie source...")
    # Sortie de la trésorerie source
    mouvement_sortie = MouvementTresorerieManager.creer_mouvement_general(
        db,
        type_mouvement="sortie",
        montant=transfert.montant,
        utilisateur_id=current_user.id,
        description=f"Transfert vers trésorerie {transfert.tresorerie_destination_id}",
        module_origine="tresorerie",
        reference_origine=f"TRANSFERT-{db_transfert.id}",
        statut="validé",
        **source_params
    )
    logging.info(f"Mouvement de sortie créé: ID {mouvement_sortie.id if mouvement_sortie else 'None'}")

    logging.info("Création du mouvement d'entrée pour la trésorerie destination...")
    # Entrée dans la trésorerie destination
    mouvement_entree = MouvementTresorerieManager.creer_mouvement_general(
        db,
        type_mouvement="entrée",
        montant=transfert.montant,
        utilisateur_id=current_user.id,
        description=f"Transfert depuis trésorerie {transfert.tresorerie_source_id}",
        module_origine="tresorerie",
        reference_origine=f"TRANSFERT-{db_transfert.id}",
        statut="validé",
        **destination_params
    )
    logging.info(f"Mouvement d'entrée créé: ID {mouvement_entree.id if mouvement_entree else 'None'}")

    logging.info("Vérification des soldes après création des mouvements...")
    # Récupérer et afficher les soldes après les mouvements
    if tresorerie_source_station:
        result = db.execute(text("""
            SELECT solde_actuel
            FROM vue_solde_tresorerie_station
            WHERE tresorerie_station_id = :tresorerie_station_id
        """), {"tresorerie_station_id": transfert.tresorerie_source_id}).fetchone()
        nouveau_solde_source = float(result.solde_actuel) if result else 0.0
        logging.info(f"Nouveau solde de la trésorerie source station: {nouveau_solde_source}")
    else:
        result = db.query(
            func.coalesce(func.sum(
                case(
                    (MouvementTresorerieModel.type_mouvement == 'entrée', MouvementTresorerieModel.montant),
                    (MouvementTresorerieModel.type_mouvement == 'sortie', -MouvementTresorerieModel.montant),
                    else_=0
                )
            ), 0).label('solde')
        ).filter(
            MouvementTresorerieModel.tresorerie_globale_id == transfert.tresorerie_source_id,
            MouvementTresorerieModel.statut == 'validé'
        ).first()
        nouveau_solde_source = float(result.solde) if result else 0.0
        logging.info(f"Nouveau solde de la trésorerie source globale: {nouveau_solde_source}")

    if tresorerie_destination_station:
        result = db.execute(text("""
            SELECT solde_actuel
            FROM vue_solde_tresorerie_station
            WHERE tresorerie_station_id = :tresorerie_station_id
        """), {"tresorerie_station_id": transfert.tresorerie_destination_id}).fetchone()
        nouveau_solde_destination = float(result.solde_actuel) if result else 0.0
        logging.info(f"Nouveau solde de la trésorerie destination station: {nouveau_solde_destination}")
    else:
        result = db.query(
            func.coalesce(func.sum(
                case(
                    (MouvementTresorerieModel.type_mouvement == 'entrée', MouvementTresorerieModel.montant),
                    (MouvementTresorerieModel.type_mouvement == 'sortie', -MouvementTresorerieModel.montant),
                    else_=0
                )
            ), 0).label('solde')
        ).filter(
            MouvementTresorerieModel.tresorerie_globale_id == transfert.tresorerie_destination_id,
            MouvementTresorerieModel.statut == 'validé'
        ).first()
        nouveau_solde_destination = float(result.solde) if result else 0.0
        logging.info(f"Nouveau solde de la trésorerie destination globale: {nouveau_solde_destination}")

    # Dans la nouvelle architecture, les soldes sont gérés automatiquement par les triggers
    # On n'a plus besoin de rafraîchir les vues matérialisées ici

    logging.info("Transfert de trésorerie terminé avec succès")
    return db_transfert


def get_transfert_tresorerie_by_id(db: Session, current_user, transfert_id: uuid.UUID):
    """Récupère un transfert de trésorerie spécifique par son ID"""
    transfert = db.query(TransfertTresorerieModel).join(
        TresorerieStationModel,
        TransfertTresorerieModel.tresorerie_source_id == TresorerieStationModel.id
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id
    ).filter(
        TransfertTresorerieModel.id == transfert_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not transfert:
        raise HTTPException(status_code=404, detail="Transfert trésorerie not found")

    return transfert


def get_solde_tresorerie(db: Session, current_user, tresorerie_id: uuid.UUID):
    """Récupère le solde d'une trésorerie globale"""
    # Vérifier que la trésorerie appartient à l'utilisateur
    tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.id == tresorerie_id,
        TresorerieModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie:
        raise HTTPException(status_code=404, detail="Trésorerie not found")

    # Récupérer le solde global de la trésorerie à partir de la vue matérialisée
    from sqlalchemy import text
    try:
        result = db.execute(text("""
            SELECT solde_tresorerie
            FROM vue_solde_tresorerie_globale
            WHERE tresorerie_id = :tresorerie_id
        """), {"tresorerie_id": tresorerie_id}).fetchone()

        solde_global = float(result.solde_tresorerie) if result else float(tresorerie.solde_initial or 0)
    except Exception as e:
        # Si la vue n'existe pas, utiliser le solde initial
        logger.warning(f"Vue vue_solde_tresorerie_globale non disponible: {e}")
        solde_global = float(tresorerie.solde_initial or 0)

    # Mettre à jour le solde dans l'objet trésorerie
    tresorerie.solde_tresorerie = solde_global

    return tresorerie


def get_tresoreries_sans_methode_paiement(db: Session, current_user):
    """Récupère les trésoreries qui n'ont aucune méthode de paiement associée"""
    from sqlalchemy import text

    # Récupérer les IDs des trésoreries (globales et stations) qui ont des méthodes de paiement associées via la table de liaison
    tresoreries_avec_methode = db.execute(text("""
        SELECT DISTINCT tmp.tresorerie_id
        FROM tresorerie_methode_paiement tmp
        JOIN tresorerie t ON tmp.tresorerie_id = t.id
        LEFT JOIN tresorerie_station ts ON t.id = ts.tresorerie_id
        LEFT JOIN station s ON ts.station_id = s.id
        WHERE (t.compagnie_id = :compagnie_id OR s.compagnie_id = :compagnie_id)
        AND tmp.actif = true
    """), {"compagnie_id": current_user.compagnie_id}).fetchall()

    ids_avec_methode = [row.tresorerie_id for row in tresoreries_avec_methode]

    # Récupérer toutes les trésoreries (globales et stations) de la compagnie
    if not ids_avec_methode:
        # Si aucune trésorerie n'a de méthode de paiement associée, retourner toutes les trésoreries
        toutes_tresoreries = db.query(TresorerieModel).filter(
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).all()

        # Ajouter aussi les trésoreries stations liées à la compagnie
        toutes_tresoreries_station = db.query(TresorerieModel).join(
            TresorerieStationModel,
            TresorerieStationModel.tresorerie_id == TresorerieModel.id
        ).join(
            Station,
            TresorerieStationModel.station_id == Station.id
        ).filter(
            Station.compagnie_id == current_user.compagnie_id
        ).distinct(TresorerieModel.id).all()

        # Combiner les deux listes et supprimer les doublons
        toutes_tresoreries.extend([t for t in toutes_tresoreries_station if t not in toutes_tresoreries])

        return toutes_tresoreries
    else:
        # Récupérer les trésoreries globales sans méthodes de paiement
        tresoreries_globales_sans_methode = db.query(TresorerieModel).filter(
            TresorerieModel.compagnie_id == current_user.compagnie_id
        ).filter(
            ~TresorerieModel.id.in_(ids_avec_methode)
        ).all()

        # Récupérer les trésoreries stations sans méthodes de paiement
        tresoreries_stations_sans_methode = db.query(TresorerieModel).join(
            TresorerieStationModel,
            TresorerieStationModel.tresorerie_id == TresorerieModel.id
        ).join(
            Station,
            TresorerieStationModel.station_id == Station.id
        ).filter(
            Station.compagnie_id == current_user.compagnie_id
        ).filter(
            ~TresorerieModel.id.in_(ids_avec_methode)
        ).distinct(TresorerieModel.id).all()

        # Combiner les deux listes et supprimer les doublons
        resultat = tresoreries_globales_sans_methode
        resultat.extend([t for t in tresoreries_stations_sans_methode if t not in resultat])

        return resultat


def get_mouvements_tresorerie_by_reference(db: Session, current_user, reference: str):
    """Récupère les mouvements de trésorerie par référence d'origine"""
    # Récupérer les mouvements de trésorerie avec la référence spécifiée
    # On joint avec les tables appropriées pour vérifier que l'utilisateur a accès aux données
    mouvements = db.query(MouvementTresorerieModel).join(
        TresorerieStationModel,
        MouvementTresorerieModel.tresorerie_station_id == TresorerieStationModel.id,
        isouter=True  # LEFT JOIN pour inclure les mouvements liés directement aux trésoreries globales
    ).join(
        TresorerieModel,
        (
            (MouvementTresorerieModel.tresorerie_globale_id == TresorerieModel.id) |
            (TresorerieStationModel.tresorerie_id == TresorerieModel.id)
        )
    ).join(
        Station,
        TresorerieStationModel.station_id == Station.id,
        isouter=True  # LEFT JOIN pour inclure les trésoreries globales non liées à une station
    ).filter(
        MouvementTresorerieModel.reference_origine == reference
    ).filter(
        (
            (TresorerieModel.compagnie_id == current_user.compagnie_id) |
            (Station.compagnie_id == current_user.compagnie_id)
        )
    ).all()

    return mouvements