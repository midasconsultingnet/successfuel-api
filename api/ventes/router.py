from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from . import schemas
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from ..services.ventes import (
    get_ventes as service_get_ventes,
    create_vente as service_create_vente,
    get_vente_by_id as service_get_vente_by_id,
    update_vente as service_update_vente,
    delete_vente as service_delete_vente,
    get_vente_details as service_get_vente_details,
    get_ventes_carburant as service_get_ventes_carburant,
    create_vente_carburant as service_create_vente_carburant,
    get_vente_carburant_by_id as service_get_vente_carburant_by_id,
    update_vente_carburant as service_update_vente_carburant,
    delete_vente_carburant as service_delete_vente_carburant,
    get_creances_employes as service_get_creances_employes,
    get_creance_employe_by_id as service_get_creance_employe_by_id
)

router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=List[schemas.VenteCreate], dependencies=[Depends(require_permission("Module Ventes Boutique"))])
async def get_ventes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_ventes(db, current_user, skip, limit)

@router.post("/", response_model=schemas.VenteCreate, dependencies=[Depends(require_permission("Module Ventes Boutique"))])
async def create_vente(
    vente: schemas.VenteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_create_vente(db, current_user, vente)

@router.get("/{vente_id}", response_model=schemas.VenteCreate, dependencies=[Depends(require_permission("Module Ventes Boutique"))])
async def get_vente_by_id(
    vente_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_vente_by_id(db, current_user, vente_id)

@router.put("/{vente_id}", response_model=schemas.VenteUpdate, dependencies=[Depends(require_permission("Module Ventes Boutique"))])
async def update_vente(
    vente_id: uuid.UUID,
    vente: schemas.VenteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_update_vente(db, current_user, vente_id, vente)

@router.delete("/{vente_id}", dependencies=[Depends(require_permission("Module Ventes Boutique"))])
async def delete_vente(
    vente_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_delete_vente(db, current_user, vente_id)

@router.get("/{vente_id}/details", response_model=List[schemas.VenteDetailCreate], dependencies=[Depends(require_permission("Module Ventes Boutique"))])
async def get_vente_details(
    vente_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_vente_details(db, current_user, vente_id, skip, limit)

# Endpoints pour les ventes de carburant
@router.get("/carburant", response_model=List[schemas.VenteCarburantCreate], dependencies=[Depends(require_permission("Module Ventes Carburant"))])
async def get_ventes_carburant(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_ventes_carburant(db, current_user, skip, limit)

@router.post("/carburant", response_model=schemas.VenteCarburantCreate, dependencies=[Depends(require_permission("Module Ventes Carburant"))])
async def create_vente_carburant(
    vente_carburant: schemas.VenteCarburantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    # Appel au service pour créer la vente carburant
    return service_create_vente_carburant(db, current_user, vente_carburant)

@router.get("/carburant/{vente_carburant_id}", response_model=schemas.VenteCarburantCreate, dependencies=[Depends(require_permission("Module Ventes Carburant"))])
async def get_vente_carburant_by_id(
    vente_carburant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_vente_carburant_by_id(db, current_user, vente_carburant_id)

@router.put("/carburant/{vente_carburant_id}", response_model=schemas.VenteCarburantUpdate, dependencies=[Depends(require_permission("Module Ventes Carburant"))])
async def update_vente_carburant(
    vente_carburant_id: uuid.UUID,
    vente_carburant: schemas.VenteCarburantUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_update_vente_carburant(db, current_user, vente_carburant_id, vente_carburant)

@router.delete("/carburant/{vente_carburant_id}", dependencies=[Depends(require_permission("Module Ventes Carburant"))])
async def delete_vente_carburant(
    vente_carburant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_delete_vente_carburant(db, current_user, vente_carburant_id)

# Endpoints pour les créances employés
@router.get("/creances_employes", response_model=List[schemas.CreanceEmployeCreate], dependencies=[Depends(require_permission("Module Ventes Carburant"))])
async def get_creances_employes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_creances_employes(db, current_user, skip, limit)

@router.get("/creances_employes/{creance_id}", response_model=schemas.CreanceEmployeCreate, dependencies=[Depends(require_permission("Module Ventes Carburant"))])
async def get_creance_employe_by_id(
    creance_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_creance_employe_by_id(db, current_user, creance_id)
