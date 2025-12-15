from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from . import schemas
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from ..services.achats import (
    get_achats as service_get_achats,
    create_achat as service_create_achat,
    get_achat_by_id as service_get_achat_by_id,
    update_achat as service_update_achat,
    delete_achat as service_delete_achat,
    get_achat_details as service_get_achat_details
)

router = APIRouter()

@router.get("/", response_model=List[schemas.AchatCreate], dependencies=[Depends(require_permission("Module Achats Boutique"))])
async def get_achats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_achats(db, skip, limit)

@router.post("/", response_model=schemas.AchatCreate, dependencies=[Depends(require_permission("Module Achats Boutique"))])
async def create_achat(
    achat: schemas.AchatCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_create_achat(db, achat)

@router.get("/{achat_id}", response_model=schemas.AchatCreate, dependencies=[Depends(require_permission("Module Achats Boutique"))])
async def get_achat_by_id(
    achat_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_achat_by_id(db, achat_id)

@router.put("/{achat_id}", response_model=schemas.AchatUpdate, dependencies=[Depends(require_permission("Module Achats Boutique"))])
async def update_achat(
    achat_id: int,
    achat: schemas.AchatUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_update_achat(db, achat_id, achat)

@router.delete("/{achat_id}", dependencies=[Depends(require_permission("Module Achats Boutique"))])
async def delete_achat(
    achat_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_delete_achat(db, achat_id)

@router.get("/{achat_id}/details", response_model=List[schemas.AchatDetailCreate], dependencies=[Depends(require_permission("Module Achats Boutique"))])
async def get_achat_details(
    achat_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    return service_get_achat_details(db, achat_id, skip, limit)
