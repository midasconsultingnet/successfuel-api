from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
from uuid import UUID
from ..database import get_db
from ..models import Compagnie as CompagnieModel, Station as StationModel, User as UserModel, Cuve, Pistolet, EtatInitialCuve
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user
from ..auth.journalisation import log_user_action
from ..auth.permission_check import check_company_access


def make_serializable(obj):
    """Convert non-serializable objects to serializable types"""
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        return obj

router = APIRouter()
security = HTTPBearer()

# Compagnie endpoints
@router.get("/", response_model=schemas.CompagnieResponse)
async def get_my_compagnie(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get the company of the current user
    compagnie = db.query(CompagnieModel).filter(CompagnieModel.id == current_user.compagnie_id).first()
    if not compagnie:
        raise HTTPException(status_code=404, detail="Compagnie not found")
    return compagnie

# Station endpoints (only for the user's company)
@router.get("/stations", response_model=List[schemas.StationResponse])
async def get_stations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get stations for the user's company
    stations = db.query(StationModel).filter(StationModel.compagnie_id == current_user.compagnie_id).offset(skip).limit(limit).all()
    return stations

@router.post("/stations", response_model=schemas.StationCreate)
async def create_station(
    station: schemas.StationCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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

    # Check if station code already exists in this company
    db_station = db.query(StationModel).filter(StationModel.code == station.code, StationModel.compagnie_id == current_user.compagnie_id).first()
    if db_station:
        raise HTTPException(status_code=400, detail="Station with this code already exists in this company")

    # Generate id and created_at server-side
    station_data = station.dict()
    station_data['id'] = uuid.uuid4()  # Generate ID server-side
    station_data['created_at'] = datetime.utcnow()  # Set created_at server-side
    station_data['compagnie_id'] = current_user.compagnie_id  # Ensure compagnie_id is set to user's company

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

@router.get("/stations/{station_id}", response_model=schemas.StationResponse)
async def get_station_by_id(
    station_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Check if the user belongs to the same company as the station
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

@router.put("/stations/{station_id}", response_model=schemas.StationResponse)
async def update_station(
    station_id: str,  # Changed to string for UUID
    station: schemas.StationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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
            StationModel.compagnie_id == current_user.compagnie_id
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
    for field, value in update_data.items():
        setattr(db_station, field, value)

    db.commit()
    db.refresh(db_station)
    return db_station

@router.delete("/stations/{station_id}")
async def delete_station(
    station_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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

    db.delete(station)
    db.commit()
    return {"message": "Station deleted successfully"}

# Cuve endpoints
@router.get("/stations/{station_id}/cuves", response_model=List[schemas.CuveResponse])
async def get_cuves(
    station_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Check if the user belongs to the same company as the station
    station = db.query(StationModel).filter(
        StationModel.id == station_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    cuves = db.query(Cuve).filter(Cuve.station_id == station_id).offset(skip).limit(limit).all()
    return cuves

@router.get("/cuves", response_model=List[schemas.CuveResponse])
async def get_all_cuves_in_company(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get all cuves for the user's company
    cuves = db.query(Cuve).join(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()
    return cuves

@router.post("/stations/{station_id}/cuves", response_model=schemas.CuveResponse)
async def create_cuve(
    station_id: str,  # Changed to string for UUID
    cuve: schemas.CuveCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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
    cuve_data['created_at'] = datetime.utcnow()  # Set created_at server-side
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

@router.get("/cuves/{cuve_id}", response_model=schemas.CuveResponse)
async def get_cuve_by_id(
    cuve_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get cuve for the user's company only
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found")
    return cuve

@router.put("/cuves/{cuve_id}", response_model=schemas.CuveResponse)
async def update_cuve(
    cuve_id: str,  # Changed to string for UUID
    cuve: schemas.CuveUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
@router.get("/cuves/{cuve_id}/pistolets", response_model=List[schemas.PistoletResponse])
async def get_pistolets(
    cuve_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get pistolets for cuve in the user's company only
    pistolets = db.query(Pistolet).join(Cuve).join(StationModel).filter(
        Pistolet.cuve_id == cuve_id,
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
    current_user = get_current_user(db, credentials.credentials)

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
    pistolet_data['created_at'] = datetime.utcnow()  # Set created_at server-side
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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
@router.post("/cuves/{cuve_id}/etat_initial", response_model=schemas.EtatInitialCuveResponse)
async def create_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    etat_initial: schemas.EtatInitialCuveCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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

    # Vérifier que l'ID utilisateur dans le payload correspond à l'utilisateur connecté
    if str(etat_initial.utilisateur_id) != str(current_user.id):
        raise HTTPException(
            status_code=400,
            detail="L'utilisateur_id dans la requête doit être l'utilisateur connecté"
        )

    # Vérifier que la hauteur de jauge initiale n'est pas supérieure à la hauteur qui correspond à la capacité maximale
    try:
        import json
        barremage = json.loads(cuve.barremage)
        # Trouver la hauteur maximale dans le barremage
        hauteurs = [item['hauteur_cm'] for item in barremage]
        max_hauteur = max(hauteurs)
        if etat_initial.hauteur_jauge_initiale > max_hauteur:
            raise HTTPException(
                status_code=400,
                detail=f"La hauteur de jauge initiale dépasse la hauteur maximale du barremage ({max_hauteur} cm)"
            )
    except (json.JSONDecodeError, KeyError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Le barremage de la cuve est mal formaté ou incorrect"
        )

    # Calculer le volume à partir de la hauteur et du barremage
    try:
        volume_calcule = cuve.calculer_volume(etat_initial.hauteur_jauge_initiale)
        # Vérifier que le volume fourni est cohérent avec le calcul basé sur le barremage
        if abs(volume_calcule - etat_initial.volume_initial_calcule) > 0.1:  # Tolérance de 0.1 litre
            raise HTTPException(
                status_code=400,
                detail=f"Le volume initial fourni ({etat_initial.volume_initial_calcule} litres) n'est pas cohérent avec le calcul basé sur le barremage ({volume_calcule} litres)"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors du calcul du volume à partir du barremage : {str(e)}"
        )

    # Vérifier que le volume initial calculé ne dépasse pas la capacité maximale
    if etat_initial.volume_initial_calcule > cuve.capacite_maximale:
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

    # Create the new initial state
    etat_initial_data = etat_initial.dict()
    etat_initial_data['id'] = uuid.uuid4()
    etat_initial_data['created_at'] = datetime.utcnow()
    etat_initial_data['cuve_id'] = cuve_id  # Ensure cuve_id is set from the URL

    db_etat_initial = EtatInitialCuve(**etat_initial_data)
    db.add(db_etat_initial)
    db.commit()
    db.refresh(db_etat_initial)

    # Log the action
    etat_initial_dict = {k: make_serializable(v) for k, v in db_etat_initial.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="etat_initial_cuve",
        donnees_apres=etat_initial_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_etat_initial

@router.get("/cuves/{cuve_id}/etat_initial", response_model=schemas.EtatInitialCuveResponse)
async def get_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).filter(
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
        raise HTTPException(status_code=404, detail="État initial de la cuve non trouvé")

    return etat_initial

@router.put("/cuves/{cuve_id}/etat_initial", response_model=schemas.EtatInitialCuveResponse)
async def update_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    etat_initial: schemas.EtatInitialCuveUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found in your company")

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
    # Pour cela, on devrait vérifier la table mouvement_stock_cuve
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT COUNT(*) FROM mouvement_stock_cuve
        WHERE cuve_id = :cuve_id AND date_mouvement > :date_initialisation
    """), {"cuve_id": cuve_id, "date_initialisation": db_etat_initial.date_initialisation})

    if result.scalar() > 0:
        raise HTTPException(
            status_code=400,
            detail="Des mouvements de stock ont déjà eu lieu après cette initialisation. La modification n'est plus autorisée."
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

    # Update the fields
    update_data = etat_initial.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_etat_initial, field, value)
    db_etat_initial.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_etat_initial)
    return db_etat_initial

@router.delete("/cuves/{cuve_id}/etat_initial")
async def delete_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Check if the cuve belongs to the user's company
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not cuve:
        raise HTTPException(status_code=404, detail="Cuve not found in your company")

    # Check if the initial state exists
    etat_initial = db.query(EtatInitialCuve).filter(
        EtatInitialCuve.cuve_id == cuve_id
    ).first()
    if not etat_initial:
        raise HTTPException(status_code=404, detail="État initial de la cuve non trouvé")

    # Vérifier que la suppression est autorisée (pas verrouillé et pas de mouvements postérieurs)
    if etat_initial.verrouille:
        raise HTTPException(
            status_code=400,
            detail="Cet état initial est verrouillé et ne peut pas être supprimé."
        )

    # Vérifier s'il existe des mouvements de stock pour cette cuve après l'initialisation
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT COUNT(*) FROM mouvement_stock_cuve
        WHERE cuve_id = :cuve_id AND date_mouvement > :date_initialisation
    """), {"cuve_id": cuve_id, "date_initialisation": etat_initial.date_initialisation})

    if result.scalar() > 0:
        raise HTTPException(
            status_code=400,
            detail="Des mouvements de stock ont déjà eu lieu après cette initialisation. La suppression n'est plus autorisée."
        )

    # Log the action before deletion
    etat_initial_dict = {k: make_serializable(v) for k, v in etat_initial.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="etat_initial_cuve",
        donnees_avant=etat_initial_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    db.delete(etat_initial)
    db.commit()
    return {"message": "État initial de la cuve supprimé avec succès"}
