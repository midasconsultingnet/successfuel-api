from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from . import schemas
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from ..services.tresoreries import (
    get_tresoreries_station as service_get_tresoreries_station,
    get_tresoreries_station_by_station as service_get_tresoreries_station_by_station,
    get_tresoreries as service_get_tresoreries,
    create_tresorerie as service_create_tresorerie,
    get_tresorerie_by_id as service_get_tresorerie_by_id,
    update_tresorerie as service_update_tresorerie,
    delete_tresorerie as service_delete_tresorerie,
    create_tresorerie_station as service_create_tresorerie_station,
    create_etat_initial_tresorerie as service_create_etat_initial_tresorerie,
    create_mouvement_tresorerie as service_create_mouvement_tresorerie,
    get_mouvements_tresorerie as service_get_mouvements_tresorerie,
    create_transfert_tresorerie as service_create_transfert_tresorerie,
    get_transferts_tresorerie as service_get_transferts_tresorerie,
    mettre_a_jour_solde_tresorerie as service_mettre_a_jour_solde_tresorerie
)

router = APIRouter()

# Tresorerie station endpoints
@router.get("/stations", response_model=List[schemas.TresorerieStationResponse], dependencies=[Depends(require_permission("Module Trésorerie"))])
async def get_tresoreries_station(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_tresoreries_station(db, current_user, skip, limit)


@router.get("/stations/{station_id}/tresoreries", response_model=List[schemas.TresorerieStationResponse], dependencies=[Depends(require_permission("Module Trésorerie"))])
async def get_tresoreries_station_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_tresoreries_station_by_station(db, current_user, station_id)

# Tresorerie endpoints (globales) - Using root path to avoid double nesting
@router.get("/", response_model=List[schemas.TresorerieResponse], dependencies=[Depends(require_permission("Module Trésorerie"))])
async def get_tresoreries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_tresoreries(db, current_user, skip, limit)

@router.post("/", response_model=schemas.TresorerieResponse, dependencies=[Depends(require_permission("Module Trésorerie"))])
async def create_tresorerie(
    tresorerie: schemas.TresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_create_tresorerie(db, current_user, tresorerie)

@router.get("/{tresorerie_id}", response_model=schemas.TresorerieResponse, dependencies=[Depends(require_permission("Module Trésorerie"))])
async def get_tresorerie_by_id(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_tresorerie_by_id(db, current_user, tresorerie_id)

@router.put("/{tresorerie_id}", response_model=schemas.TresorerieResponse, dependencies=[Depends(require_permission("Module Trésorerie"))])
async def update_tresorerie(
    tresorerie_id: uuid.UUID,
    tresorerie: schemas.TresorerieUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_update_tresorerie(db, current_user, tresorerie_id, tresorerie)

@router.delete("/{tresorerie_id}", dependencies=[Depends(require_permission("Module Trésorerie"))])
async def delete_tresorerie(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_delete_tresorerie(db, current_user, tresorerie_id)

@router.post("/stations", response_model=schemas.TresorerieStationResponse, dependencies=[Depends(require_permission("Module Trésorerie"))])
async def create_tresorerie_station(
    tresorerie_station: schemas.TresorerieStationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_create_tresorerie_station(db, current_user, tresorerie_station)

# Etat initial trésorerie endpoints
@router.post("/etats-initiaux", response_model=schemas.EtatInitialTresorerieResponse, dependencies=[Depends(require_permission("Module Trésorerie"))])
async def create_etat_initial_tresorerie(
    etat_initial: schemas.EtatInitialTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_create_etat_initial_tresorerie(db, current_user, etat_initial)

# Mouvements trésorerie endpoints
@router.post("/mouvements", response_model=schemas.MouvementTresorerieResponse, dependencies=[Depends(require_permission("Module Trésorerie"))])
async def create_mouvement_tresorerie(
    mouvement: schemas.MouvementTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_create_mouvement_tresorerie(db, current_user, mouvement)

@router.get("/mouvements", response_model=List[schemas.MouvementTresorerieResponse], dependencies=[Depends(require_permission("Module Trésorerie"))])
async def get_mouvements_tresorerie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_mouvements_tresorerie(db, current_user, skip, limit)

# Transferts trésorerie endpoints
@router.post("/transferts", response_model=schemas.TransfertTresorerieResponse, dependencies=[Depends(require_permission("Module Trésorerie"))])
async def create_transfert_tresorerie(
    transfert: schemas.TransfertTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_create_transfert_tresorerie(db, current_user, transfert)

@router.get("/transferts", response_model=List[schemas.TransfertTresorerieResponse], dependencies=[Depends(require_permission("Module Trésorerie"))])
async def get_transferts_tresorerie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_transferts_tresorerie(db, current_user, skip, limit)
