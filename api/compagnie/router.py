from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import uuid
from uuid import UUID
from ..database import get_db
from ..models import Compagnie as CompagnieModel, Station as StationModel, User as UserModel, Cuve, Pistolet, EtatInitialCuve, MouvementStockCuve, Carburant, Produit, StockProduit, PrixCarburant
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user_security
from ..auth.journalisation import log_user_action
from ..auth.permission_check import check_company_access
from ..stocks.schemas import StockCarburantInitialCreate
from .schemas_etat_initial_update import EtatInitialCuveUpdateRequest
from ..services.compagnie.etat_initial_cuve_service import update_etat_initial_cuve_service, delete_etat_initial_cuve_service, create_etat_initial_cuve_service


def make_serializable(obj):
    """Convert non-serializable objects to serializable types"""
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    elif hasattr(obj, 'quantize'):  # Check if it's a Decimal object
        from decimal import Decimal
        if isinstance(obj, Decimal):
            return float(obj)
    else:
        return obj

router = APIRouter()
security = HTTPBearer()

# Compagnie endpoints
@router.get("/",
             response_model=schemas.CompagnieResponse,
             summary="Récupérer la compagnie de l'utilisateur",
             description="Récupère les informations de la compagnie à laquelle appartient l'utilisateur connecté.",
             tags=["Compagnie"])
async def get_my_compagnie(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get the company of the current user
    compagnie = db.query(CompagnieModel).filter(CompagnieModel.id == current_user.compagnie_id).first()
    if not compagnie:
        raise HTTPException(status_code=404, detail="Compagnie not found")
    return compagnie

@router.put("/",
             response_model=schemas.CompagnieResponse,
             summary="Mettre à jour la compagnie de l'utilisateur",
             description="Met à jour les informations de la compagnie à laquelle appartient l'utilisateur connecté.",
             tags=["Compagnie"])
async def update_my_compagnie(
    compagnie_update: schemas.CompagnieUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get the company of the current user
    compagnie = db.query(CompagnieModel).filter(CompagnieModel.id == current_user.compagnie_id).first()
    if not compagnie:
        raise HTTPException(status_code=404, detail="Compagnie not found")

    # Only certain roles can update company information
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update company information"
        )

    # Log the action before update - exclude SQLAlchemy internal attributes and convert non-serializable objects
    compagnie_dict = {k: make_serializable(v) for k, v in compagnie.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="compagnie_management",
        donnees_avant=compagnie_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Update the company with the provided data
    update_data = compagnie_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(compagnie, field, value)

    db.commit()
    db.refresh(compagnie)
    return compagnie

# Station endpoints (only for the user's company)
@router.get("/stations",
             response_model=List[schemas.StationResponse],
             summary="Récupérer les stations de la compagnie",
             description="Récupère la liste des stations appartenant à la compagnie de l'utilisateur connecté.",
             tags=["Compagnie"])
async def get_stations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get stations for the user's company, excluding those with status 'supprimer'
    stations = db.query(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id,
        StationModel.statut != 'supprimer'
    ).offset(skip).limit(limit).all()
    return stations

@router.post("/stations",
             response_model=schemas.StationResponse,
             summary="Créer une nouvelle station",
             description="Crée une nouvelle station-service pour la compagnie de l'utilisateur connecté.",
             tags=["Compagnie"])
async def create_station(
    station: schemas.StationCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to this company
    check_company_access(db, current_user, str(current_user.compagnie_id))

    # Only certain roles can create stations
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create stations"
        )

    # Verify that the compagnie exists
    compagnie = db.query(CompagnieModel).filter(CompagnieModel.id == current_user.compagnie_id).first()
    if not compagnie:
        raise HTTPException(status_code=404, detail="Compagnie not found")

    # Check if station code already exists in this company for stations that are not deleted
    db_station = db.query(StationModel).filter(
        StationModel.code == station.code,
        StationModel.compagnie_id == current_user.compagnie_id,
        StationModel.statut != 'supprimer'
    ).first()
    if db_station:
        raise HTTPException(status_code=400, detail="Station with this code already exists in this company")

    # Generate id and created_at server-side
    station_data = station.dict()
    station_data['id'] = uuid.uuid4()  # Generate ID server-side
    station_data['created_at'] = datetime.now(timezone.utc)  # Set created_at server-side
    station_data['compagnie_id'] = current_user.compagnie_id  # Ensure compagnie_id is set to user's company
    station_data['statut'] = 'inactif'  # Set status to inactif by default

    # Handle coordonnees_gps: ensure it's None or a valid JSON object
    if 'coordonnees_gps' in station_data and (station_data['coordonnees_gps'] == '' or station_data['coordonnees_gps'] == {}):
        station_data['coordonnees_gps'] = None

    db_station = StationModel(**station_data)
    db.add(db_station)
    db.commit()
    db.refresh(db_station)

    # Log the action - exclude SQLAlchemy internal attributes and convert non-serializable objects
    station_dict = {k: make_serializable(v) for k, v in db_station.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="station_management",
        donnees_apres=station_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_station

@router.get("/stations-with-compagnie",
             response_model=List[schemas.StationWithCompagnieResponse],
             summary="Récupérer les stations avec les informations de la compagnie",
             description="Récupère la liste des stations avec les informations de la compagnie à laquelle elles appartiennent.",
             tags=["Compagnie"])
async def get_stations_with_compagnie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get stations with their associated company information for the user's company
    stations = db.query(StationModel).join(CompagnieModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()
    return stations

# Endpoint to get only active stations for operations like achats, ventes, inventaire
@router.get("/stations/active",
             response_model=List[schemas.StationResponse],
             summary="Récupérer les stations actives",
             description="Récupère la liste des stations actives appartenant à la compagnie de l'utilisateur connecté.",
             tags=["Compagnie"])
async def get_active_stations(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get only active stations for the user's company
    active_stations = db.query(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id,
        StationModel.statut == 'actif'
    ).all()
    return active_stations

@router.get("/stations/{station_id}",
             response_model=schemas.StationResponse,
             summary="Récupérer une station par son ID",
             description="Récupère les détails d'une station spécifique par son ID.",
             tags=["Compagnie"])
async def get_station_by_id(
    station_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to the same company as the station
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station or station.statut == 'supprimer':
        raise HTTPException(status_code=404, detail="Station not found")
    return station

# Endpoint to activate a station
@router.put("/stations/{station_id}/activate",
             response_model=schemas.StationResponse,
             summary="Activer une station",
             description="Active une station spécifique.",
             tags=["Compagnie"])
async def activate_station(
    station_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to the same company as the station
    check_company_access(db, current_user, str(current_user.compagnie_id))

    # Only certain roles can activate stations
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to activate stations"
        )

    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station or station.statut == 'supprimer':
        raise HTTPException(status_code=404, detail="Station not found")

    # Log the action before activation - exclude SQLAlchemy internal attributes and convert non-serializable objects
    station_dict = {k: make_serializable(v) for k, v in station.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="station_management",
        donnees_avant=station_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Set the status to 'actif'
    station.statut = 'actif'
    db.commit()
    db.refresh(station)
    return station

@router.put("/stations/{station_id}",
             response_model=schemas.StationResponse,
             summary="Mettre à jour une station",
             description="Met à jour les informations d'une station spécifique.",
             tags=["Compagnie"])
async def update_station(
    station_id: str,  # Changed to string for UUID
    station: schemas.StationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to the same company as the station
    check_company_access(db, current_user, str(current_user.compagnie_id))

    # Only certain roles can update stations
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update stations"
        )

    db_station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Check if the code is being changed and if the new code is already used by another station in the same company
    if station.code is not None and station.code != db_station.code:
        existing_station = db.query(StationModel).filter(
            StationModel.code == station.code,
            StationModel.compagnie_id == current_user.compagnie_id,
            StationModel.statut != 'supprimer'
        ).first()
        if existing_station:
            raise HTTPException(status_code=400, detail="Station with this code already exists in this company")

    # Log the action before update - exclude SQLAlchemy internal attributes and convert non-serializable objects
    station_dict = {k: make_serializable(v) for k, v in db_station.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="station_management",
        donnees_avant=station_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    update_data = station.dict(exclude_unset=True)

    # Handle coordonnees_gps: ensure it's None or a valid JSON object
    if 'coordonnees_gps' in update_data and (update_data['coordonnees_gps'] == '' or update_data['coordonnees_gps'] == {}):
        update_data['coordonnees_gps'] = None

    for field, value in update_data.items():
        setattr(db_station, field, value)

    db.commit()
    db.refresh(db_station)
    return db_station

@router.put("/stations/{station_id}/config",
             summary="Mettre à jour la configuration d'une station",
             description="Met à jour la configuration d'une station.",
             tags=["Compagnie"])
async def update_station_config(
    station_id: str,  # Changed to string for UUID
    config_update: schemas.StationConfigUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to the same company as the station
    check_company_access(db, current_user, str(current_user.compagnie_id))

    # Only certain roles can update station config
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update station configuration"
        )

    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Log the action before update - exclude SQLAlchemy internal attributes and convert non-serializable objects
    station_dict_before = {k: make_serializable(v) for k, v in station.__dict__.items() if not k.startswith('_')}

    # Update the config field with the values provided in the payload
    # Load the existing config as a dict
    import json

    # Convert the existing config to dict if it's a string
    if isinstance(station.config, str):
        current_config = json.loads(station.config)
    elif station.config is None:
        current_config = {"completion": {}}
    else:
        current_config = station.config

    # Update the config with the provided values
    if config_update.completion is not None:
        # Merge the completion updates into existing config
        if "completion" not in current_config:
            current_config["completion"] = {}

        # Update the specific fields in the completion section
        for key, value in config_update.completion.items():
            current_config["completion"][key] = value

    # Convert back to string for storage
    station.config = json.dumps(current_config)

    db.commit()

    # Log the action after update
    station_dict_after = {k: make_serializable(v) for k, v in station.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="station_management",
        donnees_avant=station_dict_before,
        donnees_apres=station_dict_after,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return {"message": "Configuration mise à jour avec succès", "updated_config": current_config}


@router.delete("/stations/{station_id}",
               summary="Supprimer une station",
               description="Supprime une station (suppression logique).",
               tags=["Compagnie"])
async def delete_station(
    station_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to the same company as the station
    check_company_access(db, current_user, str(current_user.compagnie_id))

    # Only certain roles can delete stations
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete stations"
        )

    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Log the action before deletion - exclude SQLAlchemy internal attributes and convert non-serializable objects
    station_dict = {k: make_serializable(v) for k, v in station.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="station_management",
        donnees_avant=station_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Instead of deleting, set the status to 'supprimer'
    station.statut = 'supprimer'
    db.commit()
    return {"message": "Station deleted successfully"}

# Cuve endpoints
@router.get("/stations/{station_id}/cuves",
           response_model=List[schemas.CuveWithCarburantResponse],
           summary="Récupérer les cuves d'une station",
           description="Récupère la liste de toutes les cuves associées à une station spécifique, avec les informations sur le carburant contenu. Cet endpoint nécessite une authentification JWT valide et l'utilisateur doit appartenir à la même compagnie que la station spécifiée.",
           tags=["Compagnie"])
async def get_cuves(
    station_id: str,  # Changed to string for UUID
    skip: int = Query(default=0, ge=0, description="Nombre d'éléments à ignorer pour la pagination"),
    limit: int = Query(default=100, ge=0, le=1000, description="Nombre maximum d'éléments à retourner, limité à 1000"),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer la liste des cuves d'une station spécifique.

    Args:
        station_id: ID de la station dont on veut récupérer les cuves
        skip: Nombre d'éléments à ignorer pour la pagination (par défaut: 0)
        limit: Nombre maximum d'éléments à retourner (par défaut: 100, max: 1000)
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        List[schemas.CuveWithCarburantResponse]: Liste des cuves avec leurs informations détaillées

    Raises:
        HTTPException 404: Si la station n'existe pas ou ne fait pas partie de la compagnie de l'utilisateur
    """
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to the same company as the station
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Get cuves for the station with their associated carburant
    cuves = db.query(Cuve).join(Carburant).filter(Cuve.station_id == station_id).offset(skip).limit(limit).all()
    return cuves

@router.get("/cuves",
           response_model=List[schemas.CuveWithStationResponse],
           summary="Récupérer toutes les cuves de la compagnie",
           description="Récupère la liste de toutes les cuves appartenant à la compagnie de l'utilisateur authentifié, avec les informations sur les stations auxquelles elles sont rattachées. Cet endpoint nécessite une authentification JWT valide.",
           tags=["Compagnie"])
async def get_all_cuves_in_company(
    skip: int = Query(default=0, ge=0, description="Nombre d'éléments à ignorer pour la pagination"),
    limit: int = Query(default=100, ge=0, le=1000, description="Nombre maximum d'éléments à retourner, limité à 1000"),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer toutes les cuves appartenant à la compagnie de l'utilisateur.

    Args:
        skip: Nombre d'éléments à ignorer pour la pagination (par défaut: 0)
        limit: Nombre maximum d'éléments à retourner (par défaut: 100, max: 1000)
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        List[schemas.CuveWithStationResponse]: Liste des cuves avec leurs stations associées

    Raises:
        HTTPException 401: Si l'utilisateur n'est pas authentifié
    """
    current_user = get_current_user_security(credentials, db)

    # Get all cuves for the user's company with their associated station
    cuves = db.query(Cuve).join(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()
    return cuves

@router.post("/stations/{station_id}/cuves",
             response_model=schemas.CuveResponse,
             summary="Créer une nouvelle cuve pour une station",
             description="Crée une nouvelle cuve associée à une station spécifique. Requiert une authentification JWT valide et des droits de gestionnaire de compagnie ou administrateur.",
             tags=["Compagnie"])
async def create_cuve(
    station_id: str,
    cuve: schemas.CuveCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Créer une nouvelle cuve associée à une station spécifique.

    Args:
        station_id: ID de la station à laquelle la cuve sera associée
        cuve: Données de la cuve à créer (nom, code, capacité, etc.)
        request: Objet requête pour journalisation
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        schemas.CuveResponse: Détails de la cuve nouvellement créée

    Raises:
        HTTPException 403: Si l'utilisateur n'a pas les permissions suffisantes
        HTTPException 404: Si la station n'existe pas ou ne fait pas partie de la compagnie de l'utilisateur
    """
    current_user = get_current_user_security(credentials, db)

    # Check if the user belongs to the same company as the station
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Only certain roles can create cuves
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create cuves"
        )

    # Generate id and created_at server-side
    cuve_data = cuve.dict()
    cuve_data['id'] = uuid.uuid4()  # Generate ID server-side
    cuve_data['created_at'] = datetime.now(timezone.utc)  # Set created_at server-side
    cuve_data['station_id'] = station_id  # Ensure station_id is set from the URL

    db_cuve = Cuve(**cuve_data)
    db.add(db_cuve)
    db.commit()
    db.refresh(db_cuve)

    # Log the action - exclude SQLAlchemy internal attributes and convert non-serializable objects
    cuve_dict = {k: make_serializable(v) for k, v in db_cuve.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="cuve_management",
        donnees_apres=cuve_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_cuve

@router.get("/cuves/{cuve_id}",
           response_model=schemas.CuveWithCarburantResponse,
           summary="Récupérer une cuve spécifique par son ID",
           description="Récupère les détails d'une cuve spécifique par son identifiant, avec les informations sur le carburant qu'elle contient. Cet endpoint nécessite une authentification JWT valide et l'utilisateur doit appartenir à la même compagnie que la cuve.",
           tags=["Compagnie"])
async def get_cuve_by_id(
    cuve_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer une cuve spécifique par son ID.

    Args:
        cuve_id: ID de la cuve à récupérer
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        schemas.CuveWithCarburantResponse: Détails de la cuve avec les informations sur le carburant

    Raises:
        HTTPException 404: Si la cuve n'existe pas ou ne fait pas partie de la compagnie de l'utilisateur
        HTTPException 401: Si l'utilisateur n'est pas authentifié
    """
    current_user = get_current_user_security(credentials, db)

    # Get cuve for the user's company only with associated carburant
    cuve = db.query(Cuve).join(StationModel).join(Carburant).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found")
    return cuve

@router.put("/cuves/{cuve_id}",
           response_model=schemas.CuveResponse,
           summary="Mettre à jour une cuve spécifique",
           description="Met à jour les détails d'une cuve spécifique par son identifiant. Requiert une authentification JWT valide et des droits de gestionnaire de compagnie ou administrateur.",
           tags=["Compagnie"])
async def update_cuve(
    cuve_id: str,  # Changed to string for UUID
    cuve: schemas.CuveUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Mettre à jour une cuve spécifique par son ID.

    Args:
        cuve_id: ID de la cuve à mettre à jour
        cuve: Données pour la mise à jour de la cuve
        request: Objet requête pour journalisation
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        schemas.CuveResponse: Détails de la cuve mise à jour

    Raises:
        HTTPException 403: Si l'utilisateur n'a pas les permissions suffisantes
        HTTPException 404: Si la cuve n'existe pas ou ne fait pas partie de la compagnie de l'utilisateur
        HTTPException 400: Si le nouveau code de cuve existe déjà dans la compagnie
    """
    current_user = get_current_user_security(credentials, db)

    # Only certain roles can update cuves
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update cuves"
        )

    db_cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not db_cuve:
        raise HTTPException(status_code=404, detail="Cuve not found")

    # Check if the code is being changed and if the new code is already used by another cuve in the same company
    if cuve.code is not None and cuve.code != db_cuve.code:
        existing_cuve = db.query(Cuve).join(StationModel).filter(
            Cuve.code == cuve.code,
            StationModel.compagnie_id == current_user.compagnie_id
        ).first()
        if existing_cuve:
            raise HTTPException(status_code=400, detail="Cuve with this code already exists in this company")

    # Log the action before update - exclude SQLAlchemy internal attributes and convert non-serializable objects
    cuve_dict = {k: make_serializable(v) for k, v in db_cuve.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="cuve_management",
        donnees_avant=cuve_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    update_data = cuve.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cuve, field, value)

    db.commit()
    db.refresh(db_cuve)
    return db_cuve

@router.delete("/cuves/{cuve_id}")
async def delete_cuve(
    cuve_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Only certain roles can delete cuves
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete cuves"
        )

    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found")

    # Log the action before deletion - exclude SQLAlchemy internal attributes and convert non-serializable objects
    cuve_dict = {k: make_serializable(v) for k, v in cuve.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="cuve_management",
        donnees_avant=cuve_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    db.delete(cuve)
    db.commit()
    return {"message": "Cuve deleted successfully"}

# Pistolet endpoints
@router.get("/cuves/{cuve_id}/pistolets", response_model=List[schemas.PistoletWithCuveResponse])
async def get_pistolets(
    cuve_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get pistolets for cuve in the user's company only with cuve information
    pistolets = db.query(Pistolet).join(Cuve).join(StationModel).filter(
        Pistolet.cuve_id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()
    return pistolets

@router.get("/pistolets-with-cuve", response_model=List[schemas.PistoletWithCuveResponse])
async def get_pistolets_with_cuve(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get pistolets with their associated cuve for the user's company
    pistolets = db.query(Pistolet).join(Cuve).join(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()
    return pistolets

@router.post("/cuves/{cuve_id}/pistolets", response_model=schemas.PistoletResponse)
async def create_pistolet(
    cuve_id: str,  # Changed to string for UUID
    pistolet: schemas.PistoletCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found")

    # Only certain roles can create pistolets
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create pistolets"
        )

    # Generate id and created_at server-side
    pistolet_data = pistolet.dict()
    pistolet_data['id'] = uuid.uuid4()  # Generate ID server-side
    pistolet_data['created_at'] = datetime.now(timezone.utc)  # Set created_at server-side
    pistolet_data['cuve_id'] = cuve_id  # Ensure cuve_id is set correctly

    db_pistolet = Pistolet(**pistolet_data)
    db.add(db_pistolet)
    db.commit()
    db.refresh(db_pistolet)

    # Log the action - exclude SQLAlchemy internal attributes and convert non-serializable objects
    pistolet_dict = {k: make_serializable(v) for k, v in db_pistolet.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="pistolet_management",
        donnees_apres=pistolet_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_pistolet

@router.get("/pistolets/{pistolet_id}", response_model=schemas.PistoletResponse)
async def get_pistolet_by_id(
    pistolet_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Get pistolet for the user's company only
    pistolet = db.query(Pistolet).join(Cuve).join(StationModel).filter(
        Pistolet.id == pistolet_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not pistolet:
        raise HTTPException(status_code=404, detail="Pistolet not found")
    return pistolet

@router.put("/pistolets/{pistolet_id}", response_model=schemas.PistoletResponse)
async def update_pistolet(
    pistolet_id: str,  # Changed to string for UUID
    pistolet: schemas.PistoletUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Only certain roles can update pistolets
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update pistolets"
        )

    db_pistolet = db.query(Pistolet).join(Cuve).join(StationModel).filter(
        Pistolet.id == pistolet_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not db_pistolet:
        raise HTTPException(status_code=404, detail="Pistolet not found")

    # Check if the number is being changed and if the new number is already used by another pistolet in the same company
    if pistolet.numero is not None and pistolet.numero != db_pistolet.numero:
        existing_pistolet = db.query(Pistolet).join(Cuve).join(StationModel).filter(
            Pistolet.numero == pistolet.numero,
            StationModel.compagnie_id == current_user.compagnie_id
        ).first()
        if existing_pistolet:
            raise HTTPException(status_code=400, detail="Pistolet with this number already exists in this company")

    # Log the action before update - exclude SQLAlchemy internal attributes and convert non-serializable objects
    pistolet_dict = {k: make_serializable(v) for k, v in db_pistolet.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="pistolet_management",
        donnees_avant=pistolet_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    update_data = pistolet.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pistolet, field, value)

    db.commit()
    db.refresh(db_pistolet)
    return db_pistolet

@router.delete("/pistolets/{pistolet_id}")
async def delete_pistolet(
    pistolet_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Only certain roles can delete pistolets
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete pistolets"
        )

    pistolet = db.query(Pistolet).join(Cuve).join(StationModel).filter(
        Pistolet.id == pistolet_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not pistolet:
        raise HTTPException(status_code=404, detail="Pistolet not found")

    # Log the action before deletion - exclude SQLAlchemy internal attributes and convert non-serializable objects
    pistolet_dict = {k: make_serializable(v) for k, v in pistolet.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="pistolet_management",
        donnees_avant=pistolet_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    db.delete(pistolet)
    db.commit()
    return {"message": "Pistolet deleted successfully"}

# États initiaux des cuves endpoints
@router.post("/cuves/{cuve_id}/etat_initial",
             response_model=schemas.EtatInitialCuveResponse,
             summary="Créer l'état initial d'une cuve",
             description="Crée l'état initial d'une cuve. Le champ cuve_id est transmis dans l'URL. Les champs date_initialisation et utilisateur_id sont automatiquement définis. Le volume_initial_calcule est automatiquement calculé à partir de la hauteur jauge et du barremage de la cuve.")
async def create_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    etat_initial_data: StockCarburantInitialCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found in your company")

    # Vérifier que le barremage est correctement renseigné avant d'initialiser le stock
    if not cuve.barremage:
        raise HTTPException(
            status_code=400,
            detail="Le barremage n'est pas défini pour cette cuve. Veuillez le définir avant d'initialiser le stock."
        )

    # Vérifier que la hauteur jauge initiale est fournie
    if etat_initial_data.hauteur_jauge_initiale is None:
        raise HTTPException(
            status_code=400,
            detail="La hauteur jauge initiale est requise"
        )

    # Vérifier que la hauteur de jauge initiale n'est pas supérieure à la hauteur qui correspond à la capacité maximale
    try:
        import json
        # Gérer les deux cas : barremage peut être une chaîne JSON ou déjà un objet Python
        if isinstance(cuve.barremage, str):
            barremage = json.loads(cuve.barremage)
        else:
            # Si cuve.barremage n'est pas une chaîne, on suppose que c'est déjà un objet Python
            barremage = cuve.barremage

        # Vérifier que le barremage est bien une liste
        if not isinstance(barremage, list):
            raise ValueError("Le barremage doit être une liste d'objets")

        # Trouver la hauteur maximale dans le barremage
        # Supporte les deux formats (hauteur_cm et hauteur)
        hauteurs = [item.get('hauteur_cm', item.get('hauteur', 0)) for item in barremage]
        max_hauteur = max(hauteurs)
        if etat_initial_data.hauteur_jauge_initiale > max_hauteur:
            raise HTTPException(
                status_code=400,
                detail=f"La hauteur de jauge initiale dépasse la hauteur maximale du barremage ({max_hauteur} cm)"
            )
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Le barremage de la cuve est mal formaté ou incorrect"
        )

    # Calculer le volume à partir de la hauteur et du barremage
    try:
        volume_calcule = cuve.calculer_volume(etat_initial_data.hauteur_jauge_initiale)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors du calcul du volume à partir du barremage : {str(e)}"
        )

    # Vérifier que le volume initial calculé ne dépasse pas la capacité maximale
    if volume_calcule > cuve.capacite_maximale:
        raise HTTPException(
            status_code=400,
            detail=f"Le volume initial dépasse la capacité maximale de la cuve ({cuve.capacite_maximale} litres)"
        )

    # Vérifier qu'il n'y a pas déjà un état initial pour cette cuve
    etat_initial_existant = db.query(EtatInitialCuve).filter(EtatInitialCuve.cuve_id == cuve_id).first()
    if etat_initial_existant:
        raise HTTPException(
            status_code=400,
            detail="Un état initial existe déjà pour cette cuve. Vous devez d'abord le supprimer ou le mettre à jour."
        )

    # Créer le stock initial carburant
    stock_initial = await create_etat_initial_cuve_service(
        cuve_id,
        etat_initial_data,
        volume_calcule,
        db,
        current_user
    )

    # Récupérer le seuil de stock minimum depuis la table stock_carburant
    from api.models.stock_carburant import StockCarburant
    stock_carburant = db.query(StockCarburant).filter(
        StockCarburant.cuve_id == stock_initial.cuve_id
    ).first()

    # Créer un dictionnaire combinant les données de l'état initial et le seuil de stock
    response_data = {
        'id': stock_initial.id,
        'cuve_id': stock_initial.cuve_id,
        'hauteur_jauge_initiale': stock_initial.hauteur_jauge_initiale,
        'volume_initial_calcule': float(stock_initial.volume_initial_calcule) if stock_initial.volume_initial_calcule else 0,
        'date_initialisation': stock_initial.date_initialisation,
        'utilisateur_id': stock_initial.utilisateur_id,
        'verrouille': stock_initial.verrouille,
        'seuil_stock_min': stock_carburant.seuil_stock_min if stock_carburant else None,
        'created_at': stock_initial.created_at,
        'updated_at': stock_initial.updated_at
    }

    # Log the action
    etat_initial_dict = {k: make_serializable(v) for k, v in stock_initial.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="etat_initial_cuve",
        donnees_apres=etat_initial_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return response_data

@router.get("/cuves/{cuve_id}/etat_initial", response_model=schemas.EtatInitialCuveWithCuveCarburantResponse)
async def get_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).join(Carburant).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found in your company")

    # Get the initial state for this cuve
    etat_initial = db.query(EtatInitialCuve).filter(
        EtatInitialCuve.cuve_id == cuve_id
    ).first()
    if not etat_initial:
        raise HTTPException(status_code=404, detail="L'état initial de la cuve n'a pas encore été défini. Veuillez d'abord initialiser le stock de cette cuve.")

    # Récupérer le seuil de stock minimum depuis la table stock_carburant
    from api.models.stock_carburant import StockCarburant
    stock_carburant = db.query(StockCarburant).filter(
        StockCarburant.cuve_id == cuve_id
    ).first()

    # Return the state with cuve and carburant information
    return {
        "id": etat_initial.id,
        "cuve_id": etat_initial.cuve_id,
        "cuve": {
            "id": cuve.id,
            "nom": cuve.nom,
            "code": cuve.code,
            "capacite_maximale": cuve.capacite_maximale,
            "carburant": {
                "id": cuve.carburant.id,
                "libelle": cuve.carburant.libelle,
                "code": cuve.carburant.code
            }
        },
        "hauteur_jauge_initiale": etat_initial.hauteur_jauge_initiale,
        "volume_initial_calcule": etat_initial.volume_initial_calcule,
        "date_initialisation": etat_initial.date_initialisation,
        "utilisateur_id": etat_initial.utilisateur_id,
        "verrouille": etat_initial.verrouille,
        "seuil_stock_min": stock_carburant.seuil_stock_min if stock_carburant else None,
        "created_at": etat_initial.created_at,
        "updated_at": etat_initial.updated_at
    }

@router.put("/cuves/{cuve_id}/etat_initial", response_model=schemas.EtatInitialCuveResponse, operation_id="update_etat_initial_cuve")
async def update_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    etat_initial_data: EtatInitialCuveUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found in your company")

    # Vérifier que le barremage est correctement renseigné
    if not cuve.barremage:
        raise HTTPException(
            status_code=400,
            detail="Le barremage n'est pas défini pour cette cuve."
        )

    # Get the existing initial state
    db_etat_initial = db.query(EtatInitialCuve).filter(
        EtatInitialCuve.cuve_id == cuve_id
    ).first()
    if not db_etat_initial:
        raise HTTPException(status_code=404, detail="État initial de la cuve non trouvé")

    # Vérifier que la modification est autorisée (pas verrouillé et pas de mouvements postérieurs)
    if db_etat_initial.verrouille:
        raise HTTPException(
            status_code=400,
            detail="Cet état initial est verrouillé et ne peut pas être modifié."
        )

    # Vérifier s'il existe des mouvements de stock pour cette cuve après l'initialisation
    # On ne considère que les mouvements non liés à l'état initial
    from sqlalchemy import text

    # Debug : afficher la date d'initialisation
    print(f"Date d'initialisation: {db_etat_initial.date_initialisation}")

    # Obtenir tous les mouvements pour cette cuve
    all_mouvements_result = db.execute(text("""
        SELECT type_mouvement, date_mouvement FROM mouvement_stock_cuve
        WHERE cuve_id = :cuve_id
        ORDER BY date_mouvement
    """), {"cuve_id": cuve_id})

    all_mouvements = all_mouvements_result.fetchall()
    print(f"Tous les mouvements pour la cuve {cuve_id}:")
    for mvt in all_mouvements:
        print(f"  - Type: {mvt[0]}, Date: {mvt[1]}")

    # Vérifier les mouvements postérieurs à l'initialisation
    result = db.execute(text("""
        SELECT COUNT(*), COUNT(*) FILTER (WHERE type_mouvement IN ('ajustement_positif', 'ajustement_negatif', 'stock_initial'))
        FROM mouvement_stock_cuve
        WHERE cuve_id = :cuve_id
        AND date_mouvement > :date_initialisation
    """), {"cuve_id": cuve_id, "date_initialisation": db_etat_initial.date_initialisation})

    count_total, count_ajustements = result.fetchone()
    print(f"Mouvements après la date d'initialisation - Total: {count_total}, Ajustements + stock_initial: {count_ajustements}")

    if count_total > count_ajustements:
        raise HTTPException(
            status_code=400,
            detail="Des mouvements de stock ont déjà eu lieu après cette initialisation. La modification n'est plus autorisée."
        )

    # Vérifier que la hauteur jauge initiale est fournie si elle est dans les données de mise à jour
    if etat_initial_data.hauteur_jauge_initiale is not None:
        try:
            import json
            # Gérer les deux cas : barremage peut être une chaîne JSON ou déjà un objet Python
            if isinstance(cuve.barremage, str):
                barremage = json.loads(cuve.barremage)
            else:
                # Si cuve.barremage n'est pas une chaîne, on suppose que c'est déjà un objet Python
                barremage = cuve.barremage

            # Vérifier que le barremage est bien une liste
            if not isinstance(barremage, list):
                raise ValueError("Le barremage doit être une liste d'objets")

            # Trouver la hauteur maximale dans le barremage
            # Supporte les deux formats (hauteur_cm et hauteur)
            hauteurs = [item.get('hauteur_cm', item.get('hauteur', 0)) for item in barremage]
            max_hauteur = max(hauteurs)
            if etat_initial_data.hauteur_jauge_initiale > max_hauteur:
                raise HTTPException(
                    status_code=400,
                    detail=f"La hauteur jauge initiale ne doit pas dépasser {max_hauteur} cm."
                )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Le format du barremage est invalide."
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    # Log the action before update
    etat_initial_dict = {k: make_serializable(v) for k, v in db_etat_initial.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="etat_initial_cuve",
        donnees_avant=etat_initial_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Calculate volume if hauteur_jauge_initiale is provided
    if 'hauteur_jauge_initiale' in etat_initial_data.dict(exclude_unset=True):
        volume_calcule = cuve.calculer_volume(etat_initial_data.hauteur_jauge_initiale)
    else:
        volume_calcule = db_etat_initial.volume_initial_calcule  # Use existing value if not updating

    # Use the service to update the initial state
    updated_etat_initial = await update_etat_initial_cuve_service(
        cuve_id,
        etat_initial_data,
        volume_calcule,
        db,
        current_user
    )

    return updated_etat_initial



@router.delete("/cuves/{cuve_id}/etat_initial", operation_id="delete_etat_initial_cuve")
async def delete_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found in your company")

    # Supprimer l'état initial
    try:
        result = await delete_etat_initial_cuve_service(
            cuve_id,
            db,
            current_user
        )

        # Log the action
        log_user_action(
            db,
            utilisateur_id=str(current_user.id),
            type_action="delete",
            module_concerne="etat_initial_cuve",
            donnees_avant={"cuve_id": cuve_id},
            ip_utilisateur=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )






# MouvementStockCuve endpoints
@router.get("/cuves/{cuve_id}/mouvements", response_model=List[schemas.MouvementStockCuveResponse])
async def get_mouvements_stock_cuve(
    cuve_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Vérifier que l'utilisateur a accès à la station de la cuve
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not cuve:
        raise HTTPException(
            status_code=404,
            detail="Cuve non trouvée ou vous n'avez pas accès à cette cuve"
        )

    # Récupérer les mouvements de stock pour la cuve avec pagination
    mouvements = db.query(MouvementStockCuve).filter(
        MouvementStockCuve.cuve_id == cuve_id
    ).order_by(MouvementStockCuve.date_mouvement.desc()).offset(skip).limit(limit).all()

    return mouvements


@router.post("/cuves/{cuve_id}/mouvements", response_model=schemas.MouvementStockCuveResponse)
async def create_mouvement_stock_cuve(
    cuve_id: str,  # Changed to string for UUID
    mouvement_data: schemas.MouvementStockCuveCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Vérifier que l'utilisateur a accès à la station de la cuve
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not cuve:
        raise HTTPException(
            status_code=404,
            detail="Cuve non trouvée ou vous n'avez pas accès à cette cuve"
        )

    # Vérifier que le type de mouvement est valide
    if mouvement_data.type_mouvement not in ["entrée", "sortie", "ajustement"]:
        raise HTTPException(
            status_code=400,
            detail="Type de mouvement invalide. Doit être 'entrée', 'sortie' ou 'ajustement'"
        )

    # Calculer les stocks avant et après
    # Récupérer le dernier mouvement pour déterminer le stock de base
    dernier_mouvement = db.query(MouvementStockCuve).filter(
        MouvementStockCuve.cuve_id == cuve_id
    ).order_by(MouvementStockCuve.date_mouvement.desc()).first()

    stock_avant = 0
    if dernier_mouvement:
        stock_avant = dernier_mouvement.stock_apres or 0
    else:
        # Si aucun mouvement existant, vérifier l'état initial de la cuve
        etat_initial = db.query(EtatInitialCuve).filter(
            EtatInitialCuve.cuve_id == cuve_id
        ).first()
        if etat_initial:
            stock_avant = etat_initial.volume_initial_calcule

    # Calculer le stock après
    if mouvement_data.type_mouvement == "entrée":
        stock_apres = stock_avant + float(mouvement_data.quantite)
    elif mouvement_data.type_mouvement == "sortie":
        stock_apres = stock_avant - float(mouvement_data.quantite)
        # Vérifier qu'on ne sort pas plus que ce qui est disponible
        if stock_apres < 0:
            raise HTTPException(
                status_code=400,
                detail="Quantité de sortie supérieure au stock disponible"
            )
    else:  # ajustement
        stock_apres = float(mouvement_data.quantite)

    # Vérifier que le stock ne dépasse pas la capacité de la cuve
    if stock_apres > cuve.capacite_maximale:
        raise HTTPException(
            status_code=400,
            detail="Le stock après mouvement dépasse la capacité maximale de la cuve"
        )

    # Créer le mouvement de stock
    nouveau_mouvement = MouvementStockCuve(
        **mouvement_data.dict(),
        stock_avant=stock_avant,
        stock_apres=stock_apres
    )

    db.add(nouveau_mouvement)
    db.commit()
    db.refresh(nouveau_mouvement)

    # Log the action after creation - exclude SQLAlchemy internal attributes and convert non-serializable objects
    mouvement_dict = {k: make_serializable(v) for k, v in nouveau_mouvement.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="mouvement_stock_cuve",
        donnees_apres=mouvement_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return nouveau_mouvement


# Produits Boutique endpoints
@router.get("/stations/{station_id}/produits-boutique", response_model=List[schemas.ProduitBoutiqueResponse])
async def get_produits_boutique_station(
    station_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(
            status_code=404,
            detail="Station non trouvée ou vous n'avez pas accès à cette station"
        )

    # Récupérer les produits boutique de la station spécifique
    produits = db.query(Produit).filter(
        Produit.station_id == station_id,
        Produit.type == "boutique"
    ).offset(skip).limit(limit).all()

    return produits


@router.get("/produits-boutique-with-station", response_model=List[schemas.ProduitBoutiqueWithStationResponse])
async def get_produits_boutique_with_station(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Récupérer les produits boutique avec leurs stations pour la compagnie de l'utilisateur
    produits = db.query(Produit).join(StationModel).filter(
        Produit.type == "boutique",
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return produits


# Endpoints pour la consultation des stocks de produits
@router.get("/stocks-produits", response_model=List[schemas.StockProduitResponse])
async def get_stocks_produits(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Récupérer les stocks de produits pour la compagnie de l'utilisateur
    stocks = db.query(StockProduit).join(Produit).join(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return stocks


@router.get("/produits-with-stock", response_model=List[schemas.ProduitWithStockResponse])
async def get_produits_with_stock(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Récupérer les produits avec leurs stocks pour la compagnie de l'utilisateur
    produits = db.query(Produit).join(StockProduit).join(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return produits


# Endpoints d'intégration avec les modules opérationnels
@router.post("/integration/ajouter-mouvement-stock", response_model=schemas.MouvementStockCuveResponse)
async def integration_ajouter_mouvement_stock(
    mouvement_data: schemas.MouvementStockCuveCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour que les modules opérationnels ajoutent un mouvement de stock
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la cuve appartient à la même compagnie que l'utilisateur
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == mouvement_data.cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not cuve:
        raise HTTPException(
            status_code=404,
            detail="Cuve non trouvée ou vous n'avez pas accès à cette cuve"
        )

    # Vérifier que le type de mouvement est valide
    if mouvement_data.type_mouvement not in ["entrée", "sortie", "ajustement"]:
        raise HTTPException(
            status_code=400,
            detail="Type de mouvement invalide. Doit être 'entrée', 'sortie' ou 'ajustement'"
        )

    # Calculer les stocks avant et après
    # Récupérer le dernier mouvement pour déterminer le stock de base
    dernier_mouvement = db.query(MouvementStockCuve).filter(
        MouvementStockCuve.cuve_id == mouvement_data.cuve_id
    ).order_by(MouvementStockCuve.date_mouvement.desc()).first()

    stock_avant = 0
    if dernier_mouvement:
        stock_avant = dernier_mouvement.stock_apres or 0
    else:
        # Si aucun mouvement existant, vérifier l'état initial de la cuve
        etat_initial = db.query(EtatInitialCuve).filter(
            EtatInitialCuve.cuve_id == mouvement_data.cuve_id
        ).first()
        if etat_initial:
            stock_avant = etat_initial.volume_initial_calcule

    # Calculer le stock après
    if mouvement_data.type_mouvement == "entrée":
        stock_apres = stock_avant + float(mouvement_data.quantite)
    elif mouvement_data.type_mouvement == "sortie":
        stock_apres = stock_avant - float(mouvement_data.quantite)
        # Vérifier qu'on ne sort pas plus que ce qui est disponible
        if stock_apres < 0:
            raise HTTPException(
                status_code=400,
                detail="Quantité de sortie supérieure au stock disponible"
            )
    else:  # ajustement
        stock_apres = float(mouvement_data.quantite)

    # Vérifier que le stock ne dépasse pas la capacité de la cuve
    if stock_apres > cuve.capacite_maximale:
        raise HTTPException(
            status_code=400,
            detail="Le stock après mouvement dépasse la capacité maximale de la cuve"
        )

    # Créer le mouvement de stock
    nouveau_mouvement = MouvementStockCuve(
        **mouvement_data.dict(),
        stock_avant=stock_avant,
        stock_apres=stock_apres
    )

    db.add(nouveau_mouvement)
    db.commit()
    db.refresh(nouveau_mouvement)

    # Log the action after creation - exclude SQLAlchemy internal attributes and convert non-serializable objects
    mouvement_dict = {k: make_serializable(v) for k, v in nouveau_mouvement.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="mouvement_stock_cuve_integration",
        donnees_apres=mouvement_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return nouveau_mouvement


@router.post("/integration/mettre-a-jour-stock-produit", response_model=schemas.StockProduitResponse)
async def integration_mettre_a_jour_stock_produit(
    produit_id: str,
    station_id: str,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    quantite_theorique: float = 0,
    quantite_reelle: float = 0
):
    """
    Endpoint pour que les modules opérationnels mettent à jour le stock d'un produit
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(
            status_code=404,
            detail="Station non trouvée ou vous n'avez pas accès à cette station"
        )

    # Vérifier que le produit appartient à la station spécifiée
    produit = db.query(Produit).filter(
        Produit.id == produit_id,
        Produit.station_id == station_id
    ).first()

    if not produit:
        raise HTTPException(
            status_code=404,
            detail="Produit non trouvé dans cette station"
        )

    # Récupérer ou créer le stock produit
    stock_produit = db.query(StockProduit).filter(
        StockProduit.produit_id == produit_id,
        StockProduit.station_id == station_id
    ).first()

    if stock_produit:
        # Mettre à jour le stock existant
        stock_produit.quantite_theorique = quantite_theorique
        stock_produit.quantite_reelle = quantite_reelle
        stock_produit.date_dernier_calcul = datetime.now(timezone.utc)
    else:
        # Créer un nouvel enregistrement de stock
        stock_produit = StockProduit(
            produit_id=produit_id,
            station_id=station_id,
            quantite_theorique=quantite_theorique,
            quantite_reelle=quantite_reelle,
            date_dernier_calcul=datetime.now(timezone.utc)
        )
        db.add(stock_produit)

    db.commit()
    db.refresh(stock_produit)

    # Log the action after update/create - exclude SQLAlchemy internal attributes and convert non-serializable objects
    stock_dict = {k: make_serializable(v) for k, v in stock_produit.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="stock_produit_integration",
        donnees_apres=stock_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return stock_produit


# Endpoints pour les stocks de cuves
@router.get("/stocks-cuves/{cuve_id}", response_model=schemas.StockCuveResponse)
async def get_stock_cuve(
    cuve_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour récupérer le stock actuel d'une cuve spécifique avec ses informations
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la cuve appartient à la même compagnie que l'utilisateur
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT * FROM vue_stock_cuve
        WHERE cuve_id = :cuve_id
        AND EXISTS (
            SELECT 1 FROM station s
            WHERE s.id = station_id AND s.compagnie_id = :compagnie_id
        )
    """), {"cuve_id": cuve_id, "compagnie_id": str(current_user.compagnie_id)})

    stock_data = result.fetchone()

    if not stock_data:
        raise HTTPException(status_code=404, detail="Cuve non trouvée ou vous n'avez pas accès à cette cuve")

    # Récupérer les informations complètes de la cuve pour obtenir le champ alert_stock
    cuve_complete = db.query(Cuve).filter(Cuve.id == cuve_id).first()

    # Convertir le résultat en dictionnaire pour le schéma
    stock_dict = {
        'cuve_id': stock_data.cuve_id,
        'station_id': stock_data.station_id,
        'carburant_id': stock_data.carburant_id,
        'cuve_nom': stock_data.cuve_nom,
        'cuve_code': stock_data.cuve_code,
        'capacite_maximale': stock_data.capacite_maximale,
        'cuve_statut': stock_data.cuve_statut,
        'alert_stock': cuve_complete.alert_stock if cuve_complete else 0,  # Récupérer le seuil d'alerte
        'stock_initial': float(stock_data.stock_initial),
        'stock_actuel': float(stock_data.stock_actuel),
        'derniere_date_mouvement': stock_data.derniere_date_mouvement,
        'date_dernier_mouvement': stock_data.date_dernier_mouvement,
        'carburant_libelle': stock_data.carburant_libelle,
        'carburant_code': stock_data.carburant_code,
        'station_nom': stock_data.station_nom,
        'station_code': stock_data.station_code,
        'compagnie_nom': stock_data.compagnie_nom
    }

    return stock_dict


@router.get("/stocks-cuves", response_model=List[schemas.StockCuveResponse])
async def get_all_stocks_cuves(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour récupérer tous les stocks de cuves pour la compagnie de l'utilisateur
    """
    current_user = get_current_user_security(credentials, db)

    from sqlalchemy import text
    result = db.execute(text("""
        SELECT * FROM vue_stock_cuve
        WHERE EXISTS (
            SELECT 1 FROM station s
            WHERE s.id = station_id AND s.compagnie_id = :compagnie_id
        )
        ORDER BY cuve_nom
        LIMIT :limit OFFSET :offset
    """), {"compagnie_id": str(current_user.compagnie_id), "limit": limit, "offset": skip})

    stocks_data = result.fetchall()

    # Récupérer toutes les cuves de la compagnie pour obtenir leurs seuils d'alerte
    cuves_compagnie = db.query(Cuve).join(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).all()

    # Créer un dictionnaire pour un accès rapide aux seuils d'alerte
    cuves_alertes = {str(cuve.id): cuve.alert_stock for cuve in cuves_compagnie}

    stocks = []
    for stock_row in stocks_data:
        stock_dict = {
            'cuve_id': stock_row.cuve_id,
            'station_id': stock_row.station_id,
            'carburant_id': stock_row.carburant_id,
            'cuve_nom': stock_row.cuve_nom,
            'cuve_code': stock_row.cuve_code,
            'capacite_maximale': stock_row.capacite_maximale,
            'cuve_statut': stock_row.cuve_statut,
            'alert_stock': cuves_alertes.get(str(stock_row.cuve_id), 0),  # Récupérer le seuil d'alerte
            'stock_initial': float(stock_row.stock_initial),
            'stock_actuel': float(stock_row.stock_actuel),
            'derniere_date_mouvement': stock_row.derniere_date_mouvement,
            'date_dernier_mouvement': stock_row.date_dernier_mouvement,
            'carburant_libelle': stock_row.carburant_libelle,
            'carburant_code': stock_row.carburant_code,
            'station_nom': stock_row.station_nom,
            'station_code': stock_row.station_code,
            'compagnie_nom': stock_row.compagnie_nom
        }
        stocks.append(stock_dict)

    return stocks


# Endpoints pour la gestion des prix de carburant
@router.post("/prix-carburants", response_model=schemas.PrixCarburantResponse)
async def create_prix_carburant(
    prix_data: schemas.PrixCarburantCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour créer ou mettre à jour le prix d'un carburant pour une station
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(StationModel).filter(
        StationModel.id == prix_data.station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou vous n'avez pas accès à cette station")

    # Vérifier si un prix existe déjà pour ce couple carburant/station
    prix_existing = db.query(PrixCarburant).filter(
        PrixCarburant.carburant_id == prix_data.carburant_id,
        PrixCarburant.station_id == prix_data.station_id
    ).first()

    if prix_existing:
        # Mettre à jour les prix existants
        if prix_data.prix_achat is not None:
            prix_existing.prix_achat = prix_data.prix_achat
        if prix_data.prix_vente is not None:
            prix_existing.prix_vente = prix_data.prix_vente
        db.commit()
        db.refresh(prix_existing)
        return prix_existing
    else:
        # Créer un nouveau prix
        prix_carburant = PrixCarburant(
            carburant_id=prix_data.carburant_id,
            station_id=prix_data.station_id,
            prix_achat=prix_data.prix_achat,
            prix_vente=prix_data.prix_vente
        )
        db.add(prix_carburant)
        db.commit()
        db.refresh(prix_carburant)
        return prix_carburant


@router.get("/prix-carburants/{carburant_id}/{station_id}", response_model=schemas.PrixCarburantResponse)
async def get_prix_carburant(
    carburant_id: str,  # UUID du carburant
    station_id: str,    # UUID de la station
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour récupérer le prix d'un carburant pour une station spécifique
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(StationModel).filter(
        StationModel.id == UUID(station_id),
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou vous n'avez pas accès à cette station")

    prix_carburant = db.query(PrixCarburant).filter(
        PrixCarburant.carburant_id == UUID(carburant_id),
        PrixCarburant.station_id == UUID(station_id)
    ).first()

    if not prix_carburant:
        raise HTTPException(status_code=404, detail="Prix de carburant non trouvé")

    return prix_carburant


@router.put("/prix-carburants/{carburant_id}/{station_id}", response_model=schemas.PrixCarburantResponse)
async def update_prix_carburant(
    carburant_id: str,   # UUID du carburant
    station_id: str,     # UUID de la station
    prix_update: schemas.PrixCarburantUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour mettre à jour le prix d'un carburant pour une station spécifique
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(StationModel).filter(
        StationModel.id == UUID(station_id),
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou vous n'avez pas accès à cette station")

    prix_carburant = db.query(PrixCarburant).filter(
        PrixCarburant.carburant_id == UUID(carburant_id),
        PrixCarburant.station_id == UUID(station_id)
    ).first()

    if not prix_carburant:
        raise HTTPException(status_code=404, detail="Prix de carburant non trouvé")

    # Mettre à jour les prix
    if prix_update.prix_achat is not None:
        prix_carburant.prix_achat = prix_update.prix_achat
    if prix_update.prix_vente is not None:
        prix_carburant.prix_vente = prix_update.prix_vente

    db.commit()
    db.refresh(prix_carburant)
    return prix_carburant


@router.get("/stations/{station_id}/carburants", response_model=List[schemas.PrixCarburantWithCarburantResponse])
async def get_all_prix_carburants_station(
    station_id: str,  # UUID de la station
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour récupérer tous les prix de carburants pour une station spécifique
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(StationModel).filter(
        StationModel.id == UUID(station_id),
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou vous n'avez pas accès à cette station")

    from sqlalchemy import text
    result = db.execute(text("""
        SELECT
            pc.id,
            pc.carburant_id,
            pc.station_id,
            pc.prix_achat,
            pc.prix_vente,
            pc.created_at,
            c.libelle AS carburant_libelle,
            c.code AS carburant_code
        FROM prix_carburant pc
        JOIN carburant c ON pc.carburant_id = c.id
        WHERE pc.station_id = :station_id
        ORDER BY c.libelle
        LIMIT :limit OFFSET :offset
    """), {"station_id": station_id, "limit": limit, "offset": skip})

    prix_carburants_data = result.fetchall()

    prix_carburants = []
    for prix_row in prix_carburants_data:
        prix_dict = {
            'id': prix_row.id,
            'carburant_id': prix_row.carburant_id,
            'station_id': prix_row.station_id,
            'prix_achat': float(prix_row.prix_achat) if prix_row.prix_achat else None,
            'prix_vente': float(prix_row.prix_vente) if prix_row.prix_vente else None,
            'created_at': prix_row.created_at,
            'carburant_libelle': prix_row.carburant_libelle,
            'carburant_code': prix_row.carburant_code
        }
        prix_carburants.append(prix_dict)

    return prix_carburants


# Endpoint pour récupérer tous les pistolets d'une station spécifique
@router.get("/stations/{station_id}/pistolets", response_model=List[schemas.PistoletWithCuveForStationResponse])
async def get_pistolets_station(
    station_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou vous n'avez pas accès à cette station")

    # Récupérer les pistolets avec leurs cuves pour la station spécifiée
    pistolets = db.query(Pistolet).join(Cuve).filter(
        Cuve.station_id == station_id
    ).offset(skip).limit(limit).all()

    return pistolets
