from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
from uuid import UUID
from ..database import get_db
from ..models import Compagnie as CompagnieModel, Station as StationModel, User as UserModel, Cuve, Pistolet, EtatInitialCuve, MouvementStockCuve, Carburant, Produit, StockProduit, PrixCarburant
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

    # Get stations for the user's company, excluding those with status 'supprimer'
    stations = db.query(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id,
        StationModel.statut != 'supprimer'
    ).offset(skip).limit(limit).all()
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
    station_data['statut'] = 'inactif'  # Set status to inactif by default

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

@router.get("/stations-with-compagnie", response_model=List[schemas.StationWithCompagnieResponse])
async def get_stations_with_compagnie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get stations with their associated company information for the user's company
    stations = db.query(StationModel).join(CompagnieModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()
    return stations

# Endpoint to get only active stations for operations like achats, ventes, inventaire
@router.get("/stations/active", response_model=List[schemas.StationResponse])
async def get_active_stations(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get only active stations for the user's company
    active_stations = db.query(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id,
        StationModel.statut == 'actif'
    ).all()
    return active_stations

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
    if not station or station.statut == 'supprimer':
        raise HTTPException(status_code=404, detail="Station not found")
    return station

# Endpoint to activate a station
@router.put("/stations/{station_id}/activate")
async def activate_station(
    station_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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
    return {"message": "Station activated successfully"}

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

    # Instead of deleting, set the status to 'supprimer'
    station.statut = 'supprimer'
    db.commit()
    return {"message": "Station deleted successfully"}

# Cuve endpoints
@router.get("/stations/{station_id}/cuves", response_model=List[schemas.CuveWithCarburantResponse])
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

    # Get cuves for the station with their associated carburant
    cuves = db.query(Cuve).join(Carburant).filter(Cuve.station_id == station_id).offset(skip).limit(limit).all()
    return cuves

@router.get("/cuves", response_model=List[schemas.CuveWithStationResponse])
async def get_all_cuves_in_company(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get all cuves for the user's company with their associated station
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

@router.get("/cuves/{cuve_id}", response_model=schemas.CuveWithCarburantResponse)
async def get_cuve_by_id(
    cuve_id: str,  # Changed to string for UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Get cuve for the user's company only with associated carburant
    cuve = db.query(Cuve).join(StationModel).join(Carburant).filter(
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
@router.get("/cuves/{cuve_id}/pistolets", response_model=List[schemas.PistoletWithCuveResponse])
async def get_pistolets(
    cuve_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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

@router.post("/initialiser-stock-carburant", response_model=schemas.EtatInitialCuveResponse)
async def initialiser_stock_carburant(
    etat_initial_data: schemas.EtatInitialCuveCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que l'utilisateur a accès à la station de la cuve
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == etat_initial_data.cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not cuve:
        raise HTTPException(
            status_code=404,
            detail="Cuve non trouvée ou vous n'avez pas accès à cette cuve"
        )

    # Vérifier qu'il n'existe pas déjà un état initial pour cette cuve
    etat_initial_existant = db.query(EtatInitialCuve).filter(
        EtatInitialCuve.cuve_id == etat_initial_data.cuve_id
    ).first()

    if etat_initial_existant:
        raise HTTPException(
            status_code=400,
            detail="Un état initial existe déjà pour cette cuve"
        )

    # Vérifiez que le volume initial ne dépasse pas la capacité maximale de la cuve
    if etat_initial_data.volume_initial_calcule > cuve.capacite_maximale:
        raise HTTPException(
            status_code=400,
            detail="Le volume initial dépasse la capacité maximale de la cuve"
        )

    # Créer l'état initial
    nouvel_etat_initial = EtatInitialCuve(
        **etat_initial_data.dict(),
        utilisateur_id=etat_initial_data.utilisateur_id  # Passer l'utilisateur qui initialise
    )

    db.add(nouvel_etat_initial)
    db.commit()
    db.refresh(nouvel_etat_initial)

    # Log the action after creation - exclude SQLAlchemy internal attributes and convert non-serializable objects
    etat_initial_dict = {k: make_serializable(v) for k, v in nouvel_etat_initial.__dict__.items() if not k.startswith('_')}

    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="etat_initial_cuve",
        donnees_apres=etat_initial_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return nouvel_etat_initial


@router.delete("/cuves/{cuve_id}/etat_initial")
async def delete_etat_initial_cuve(
    cuve_id: str,  # Changed to string for UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Check if user has access to the station that owns the cuve
    cuve = db.query(Cuve).join(StationModel).filter(
        Cuve.id == cuve_id,
        StationModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not cuve:
        raise HTTPException(
            status_code=404,
            detail="Cuve non trouvée ou vous n'avez pas accès à cette cuve"
        )

    etat_initial = db.query(EtatInitialCuve).filter(
        EtatInitialCuve.cuve_id == cuve_id
    ).first()

    if not etat_initial or etat_initial.verrouille:
        raise HTTPException(
            status_code=404 if not etat_initial else 400,
            detail="État initial non trouvé ou verrouillé" if etat_initial else "État initial non trouvé"
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


# MouvementStockCuve endpoints
@router.get("/cuves/{cuve_id}/mouvements", response_model=List[schemas.MouvementStockCuveResponse])
async def get_mouvements_stock_cuve(
    cuve_id: str,  # Changed to string for UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

    # Récupérer les produits avec leurs stocks pour la compagnie de l'utilisateur
    produits = db.query(Produit).join(StockProduit).join(StationModel).filter(
        StationModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return produits


# Endpoints d'intégration avec les modules opérationnels
@router.post("/integration/ajouter-mouvement-stock")
async def integration_ajouter_mouvement_stock(
    mouvement_data: schemas.MouvementStockCuveCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour que les modules opérationnels ajoutent un mouvement de stock
    """
    current_user = get_current_user(db, credentials.credentials)

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


@router.post("/integration/mettre-a-jour-stock-produit")
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
    current_user = get_current_user(db, credentials.credentials)

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
        stock_produit.date_dernier_calcul = datetime.utcnow()
    else:
        # Créer un nouvel enregistrement de stock
        stock_produit = StockProduit(
            produit_id=produit_id,
            station_id=station_id,
            quantite_theorique=quantite_theorique,
            quantite_reelle=quantite_reelle,
            date_dernier_calcul=datetime.utcnow()
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
    current_user = get_current_user(db, credentials.credentials)

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

    # Convertir le résultat en dictionnaire pour le schéma
    stock_dict = {
        'cuve_id': stock_data.cuve_id,
        'station_id': stock_data.station_id,
        'carburant_id': stock_data.carburant_id,
        'cuve_nom': stock_data.cuve_nom,
        'cuve_code': stock_data.cuve_code,
        'capacite_maximale': stock_data.capacite_maximale,
        'cuve_statut': stock_data.cuve_statut,
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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
    current_user = get_current_user(db, credentials.credentials)

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
