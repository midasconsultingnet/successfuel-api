from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Tiers as TiersModel
from . import schemas
from ..utils.pagination import PaginatedResponse
from ..utils.filters import TiersFilterParams
from ..services.pagination_service import apply_filters_and_pagination, apply_specific_filters
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=PaginatedResponse[schemas.TiersCreate])
async def get_tiers(
    filters: TiersFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Construction de la requête avec les filtres
    query = db.query(TiersModel)

    # Application des filtres spécifiques
    query = apply_specific_filters(query, filters, TiersModel)

    # S'assurer que l'utilisateur ne voit que les tiers de sa compagnie
    query = query.filter(TiersModel.compagnie_id == current_user.compagnie_id)

    # Application du tri
    if filters.sort_by:
        sort_field = getattr(TiersModel, filters.sort_by, None)
        if sort_field:
            if filters.sort_order == 'desc':
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    tiers = query.offset(filters.skip).limit(filters.limit).all()

    # Détermination s'il y a plus d'éléments
    has_more = (filters.skip + filters.limit) < total

    return PaginatedResponse(
        items=tiers,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
        has_more=has_more
    )

@router.post("/", response_model=schemas.TiersCreate)
async def create_tiers(
    tiers: schemas.TiersCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Check if tiers already exists based on name and type
    db_tiers = db.query(TiersModel).filter(
        TiersModel.nom == tiers.nom,
        TiersModel.type == tiers.type
    ).first()
    if db_tiers:
        raise HTTPException(status_code=400, detail="Tiers with this name and type already exists")
    
    # Create the tiers based on type
    db_tiers = TiersModel(**tiers.dict())
    db.add(db_tiers)
    db.commit()
    db.refresh(db_tiers)
    
    return db_tiers

@router.get("/{tiers_id}", response_model=schemas.TiersCreate)
async def get_tiers_by_id(
    tiers_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    tiers = db.query(TiersModel).filter(TiersModel.id == tiers_id).first()
    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")
    return tiers

@router.put("/{tiers_id}", response_model=schemas.TiersUpdate)
async def update_tiers(
    tiers_id: int, 
    tiers: schemas.TiersUpdate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_tiers = db.query(TiersModel).filter(TiersModel.id == tiers_id).first()
    if not db_tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")
    
    update_data = tiers.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tiers, field, value)
    
    db.commit()
    db.refresh(db_tiers)
    return db_tiers

@router.delete("/{tiers_id}")
async def delete_tiers(
    tiers_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    tiers = db.query(TiersModel).filter(TiersModel.id == tiers_id).first()
    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")
    
    db.delete(tiers)
    db.commit()
    return {"message": "Tiers deleted successfully"}

@router.get("/type/{type_tiers}", response_model=PaginatedResponse[schemas.TiersCreate])
async def get_tiers_by_type(
    type_tiers: str,
    filters: TiersFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Construction de la requête avec les filtres
    query = db.query(TiersModel).filter(TiersModel.type == type_tiers)

    # Application des filtres spécifiques
    query = apply_specific_filters(query, filters, TiersModel)

    # S'assurer que l'utilisateur ne voit que les tiers de sa compagnie
    query = query.filter(TiersModel.compagnie_id == current_user.compagnie_id)

    # Application du tri
    if filters.sort_by:
        sort_field = getattr(TiersModel, filters.sort_by, None)
        if sort_field:
            if filters.sort_order == 'desc':
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    tiers = query.offset(filters.skip).limit(filters.limit).all()

    # Détermination s'il y a plus d'éléments
    has_more = (filters.skip + filters.limit) < total

    return PaginatedResponse(
        items=tiers,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
        has_more=has_more
    )
