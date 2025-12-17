from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Immobilisation as ImmobilisationModel, MouvementImmobilisation as MouvementImmobilisationModel
from . import schemas
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..rbac_decorators import require_permission
from ..auth.auth_handler import get_current_user_security
from ..models.user import User as UserModel
from ..models.affectation_utilisateur_station import AffectationUtilisateurStation as AffectationUtilisateurStationModel


router = APIRouter()
security = HTTPBearer()

# Endpoints pour les immobilisations
@router.get("/", response_model=List[schemas.ImmobilisationResponse])
async def get_immobilisations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Immobilisations"))
):
    from ..models.compagnie import Station
    # Vérifier les droits d'accès selon le rôle
    if current_user.role == "utilisateur_compagnie":
        # Pour un utilisateur compagnie, récupérer uniquement les immobilisations des stations auxquelles il est affecté
        station_ids = db.query(AffectationUtilisateurStationModel.station_id).filter(
            AffectationUtilisateurStationModel.utilisateur_id == current_user.id
        ).all()

        if not station_ids:
            return []  # Aucune station assignée à l'utilisateur

        station_ids = [sid[0] for sid in station_ids]  # Extraire les UUIDs des résultats
        immobilisations = db.query(ImmobilisationModel).filter(
            ImmobilisationModel.station_id.in_(station_ids)
        ).offset(skip).limit(limit).all()
    else:
        # Pour un gérant compagnie ou autre rôle, récupérer toutes les immobilisations de la compagnie
        immobilisations = db.query(ImmobilisationModel).join(Station).filter(
            Station.compagnie_id == current_user.compagnie_id
        ).offset(skip).limit(limit).all()

    return immobilisations

@router.post("/", response_model=schemas.ImmobilisationResponse)
async def create_immobilisation(
    immobilisation: schemas.ImmobilisationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Immobilisations"))
):
    from ..models.compagnie import Station
    # Vérifier les permissions d'accès à la station
    station = db.query(Station).filter(Station.id == immobilisation.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée")

    if current_user.role == "utilisateur_compagnie":
        # Vérifier que l'utilisateur est affecté à cette station
        affectation = db.query(AffectationUtilisateurStationModel).filter(
            AffectationUtilisateurStationModel.utilisateur_id == current_user.id,
            AffectationUtilisateurStationModel.station_id == immobilisation.station_id
        ).first()

        if not affectation:
            raise HTTPException(status_code=403, detail="Accès refusé : vous n'êtes pas affecté à cette station")

    # Vérifier que l'utilisateur appartient à la même compagnie que la station
    if str(station.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : la station n'appartient pas à votre compagnie")

    # Vérifier que le code est unique pour la station
    existing_immobilisation = db.query(ImmobilisationModel).filter(
        ImmobilisationModel.code == immobilisation.code,
        ImmobilisationModel.station_id == immobilisation.station_id
    ).first()

    if existing_immobilisation:
        raise HTTPException(status_code=400, detail="Immobilisation avec ce code existe déjà pour cette station")

    # Créer l'immobilisation
    db_immobilisation = ImmobilisationModel(
        nom=immobilisation.nom,
        description=immobilisation.description,
        code=immobilisation.code,
        type=immobilisation.type,
        date_acquisition=immobilisation.date_acquisition,
        valeur_origine=immobilisation.valeur_origine,
        valeur_nette=immobilisation.valeur_origine,  # Initialement, la valeur nette est égale à la valeur d'origine
        station_id=immobilisation.station_id
    )

    db.add(db_immobilisation)
    db.commit()
    db.refresh(db_immobilisation)

    return db_immobilisation

@router.get("/{immobilisation_id}", response_model=schemas.ImmobilisationResponse)
async def get_immobilisation_by_id(
    immobilisation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Immobilisations"))
):
    from ..models.compagnie import Station
    import uuid
    # Convertir le string en UUID pour la requête
    try:
        immobilisation_uuid = uuid.UUID(immobilisation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'immobilisation invalide")

    immobilisation_station = db.query(ImmobilisationModel, Station).join(Station).filter(
        ImmobilisationModel.id == immobilisation_uuid
    ).first()

    if not immobilisation_station:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    immobilisation, station = immobilisation_station

    # Vérifier les permissions d'accès selon le rôle
    if current_user.role == "utilisateur_compagnie":
        # Vérifier que l'utilisateur est affecté à la station de l'immobilisation
        affectation = db.query(AffectationUtilisateurStationModel).filter(
            AffectationUtilisateurStationModel.utilisateur_id == current_user.id,
            AffectationUtilisateurStationModel.station_id == immobilisation.station_id
        ).first()

        if not affectation:
            raise HTTPException(status_code=403, detail="Accès refusé : vous n'êtes pas affecté à la station de cette immobilisation")

    # Vérifier que l'immobilisation appartient à la même compagnie que l'utilisateur
    if str(station.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : cette immobilisation n'appartient pas à votre compagnie")

    return immobilisation

@router.put("/{immobilisation_id}", response_model=schemas.ImmobilisationUpdate)
async def update_immobilisation(
    immobilisation_id: str,
    immobilisation: schemas.ImmobilisationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Immobilisations"))
):
    from ..models.compagnie import Station
    import uuid
    # Convertir le string en UUID pour la requête
    try:
        immobilisation_uuid = uuid.UUID(immobilisation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'immobilisation invalide")

    immobilisation_station = db.query(ImmobilisationModel, Station).join(Station).filter(
        ImmobilisationModel.id == immobilisation_uuid
    ).first()
    if not immobilisation_station:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    db_immobilisation, station = immobilisation_station

    # Vérifier les permissions d'accès selon le rôle
    if current_user.role == "utilisateur_compagnie":
        # Vérifier que l'utilisateur est affecté à la station de l'immobilisation
        affectation = db.query(AffectationUtilisateurStationModel).filter(
            AffectationUtilisateurStationModel.utilisateur_id == current_user.id,
            AffectationUtilisateurStationModel.station_id == db_immobilisation.station_id
        ).first()

        if not affectation:
            raise HTTPException(status_code=403, detail="Accès refusé : vous n'êtes pas affecté à la station de cette immobilisation")

    # Vérifier que l'immobilisation appartient à la même compagnie que l'utilisateur
    if str(station.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : cette immobilisation n'appartient pas à votre compagnie")

    update_data = immobilisation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_immobilisation, field, value)

    db.commit()
    db.refresh(db_immobilisation)
    return db_immobilisation

@router.delete("/{immobilisation_id}")
async def delete_immobilisation(
    immobilisation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Immobilisations"))
):
    from ..models.compagnie import Station
    import uuid
    # Convertir le string en UUID pour la requête
    try:
        immobilisation_uuid = uuid.UUID(immobilisation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'immobilisation invalide")

    immobilisation_station = db.query(ImmobilisationModel, Station).join(Station).filter(
        ImmobilisationModel.id == immobilisation_uuid
    ).first()
    if not immobilisation_station:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    immobilisation, station = immobilisation_station

    # Vérifier les permissions d'accès selon le rôle
    if current_user.role == "utilisateur_compagnie":
        # Vérifier que l'utilisateur est affecté à la station de l'immobilisation
        affectation = db.query(AffectationUtilisateurStationModel).filter(
            AffectationUtilisateurStationModel.utilisateur_id == current_user.id,
            AffectationUtilisateurStationModel.station_id == immobilisation.station_id
        ).first()

        if not affectation:
            raise HTTPException(status_code=403, detail="Accès refusé : vous n'êtes pas affecté à la station de cette immobilisation")

    # Vérifier que l'immobilisation appartient à la même compagnie que l'utilisateur
    if str(station.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : cette immobilisation n'appartient pas à votre compagnie")

    # Vérifier qu'il n'y a pas de mouvements associés avant de supprimer
    mouvements = db.query(MouvementImmobilisationModel).filter(
        MouvementImmobilisationModel.immobilisation_id == immobilisation_id
    ).count()

    if mouvements > 0:
        raise HTTPException(status_code=400, detail="Impossible de supprimer une immobilisation avec des mouvements associés")

    db.delete(immobilisation)
    db.commit()
    return {"message": "Immobilisation deleted successfully"}

# Endpoints pour les mouvements d'immobilisations
@router.get("/{immobilisation_id}/mouvements", response_model=List[schemas.MouvementImmobilisationResponse])
async def get_mouvements_immobilisation(
    immobilisation_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Immobilisations"))
):
    from ..models.compagnie import Station
    import uuid
    # Convertir le string en UUID pour la requête
    try:
        immobilisation_uuid = uuid.UUID(immobilisation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'immobilisation invalide")

    # Vérifier que l'utilisateur a accès à cette immobilisation
    immobilisation_station = db.query(ImmobilisationModel, Station).join(Station).filter(
        ImmobilisationModel.id == immobilisation_uuid
    ).first()

    if not immobilisation_station:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    immobilisation, station = immobilisation_station

    # Vérifier les permissions d'accès selon le rôle
    if current_user.role == "utilisateur_compagnie":
        # Vérifier que l'utilisateur est affecté à la station de l'immobilisation
        affectation = db.query(AffectationUtilisateurStationModel).filter(
            AffectationUtilisateurStationModel.utilisateur_id == current_user.id,
            AffectationUtilisateurStationModel.station_id == immobilisation.station_id
        ).first()

        if not affectation:
            raise HTTPException(status_code=403, detail="Accès refusé : vous n'êtes pas affecté à la station de cette immobilisation")

    # Vérifier que l'immobilisation appartient à la même compagnie que l'utilisateur
    if str(station.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : cette immobilisation n'appartient pas à votre compagnie")

    mouvements = db.query(MouvementImmobilisationModel).filter(
        MouvementImmobilisationModel.immobilisation_id == immobilisation_id
    ).offset(skip).limit(limit).all()
    return mouvements

@router.post("/{immobilisation_id}/mouvements", response_model=schemas.MouvementImmobilisationResponse)
async def create_mouvement_immobilisation(
    immobilisation_id: str,
    mouvement: schemas.MouvementImmobilisationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Immobilisations"))
):
    from ..models.compagnie import Station
    import uuid
    # Convertir le string en UUID pour la requête
    try:
        immobilisation_uuid = uuid.UUID(immobilisation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'immobilisation invalide")

    # Vérifier que l'immobilisation existe et que l'utilisateur y a accès
    immobilisation_station = db.query(ImmobilisationModel, Station).join(Station).filter(
        ImmobilisationModel.id == immobilisation_uuid
    ).first()
    if not immobilisation_station:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    immobilisation, station = immobilisation_station

    # Vérifier les permissions d'accès selon le rôle
    if current_user.role == "utilisateur_compagnie":
        # Vérifier que l'utilisateur est affecté à la station de l'immobilisation
        affectation = db.query(AffectationUtilisateurStationModel).filter(
            AffectationUtilisateurStationModel.utilisateur_id == current_user.id,
            AffectationUtilisateurStationModel.station_id == immobilisation.station_id
        ).first()

        if not affectation:
            raise HTTPException(status_code=403, detail="Accès refusé : vous n'êtes pas affecté à la station de cette immobilisation")

    # Vérifier que l'immobilisation appartient à la même compagnie que l'utilisateur
    if str(station.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : cette immobilisation n'appartient pas à votre compagnie")

    # Créer le mouvement d'immobilisation
    db_mouvement = MouvementImmobilisationModel(
        immobilisation_id=immobilisation_id,
        type_mouvement=mouvement.type_mouvement,
        date_mouvement=mouvement.date_mouvement,
        description=mouvement.description,
        valeur_variation=mouvement.valeur_variation,
        valeur_apres_mouvement=mouvement.valeur_apres_mouvement,
        utilisateur_id=current_user.id,  # Use current user's ID instead of the one from the request
        reference_document=mouvement.reference_document
    )

    # Mettre à jour la valeur nette de l'immobilisation selon le type de mouvement
    if mouvement.type_mouvement == "amortissement":
        # Appliquer l'amortissement
        if mouvement.valeur_variation and immobilisation.valeur_nette:
            immobilisation.valeur_nette -= mouvement.valeur_variation
    elif mouvement.type_mouvement == "amélioration":
        # Ajouter la valeur de l'amélioration
        if mouvement.valeur_variation and immobilisation.valeur_nette:
            immobilisation.valeur_nette += mouvement.valeur_variation
    elif mouvement.type_mouvement == "cession" or mouvement.type_mouvement == "sortie":
        # Déprécier l'immobilisation lors d'une cession ou sortie
        immobilisation.statut = "cessionné" if mouvement.type_mouvement == "cession" else "hors_service"

    db.add(db_mouvement)
    db.commit()
    db.refresh(db_mouvement)

    return db_mouvement