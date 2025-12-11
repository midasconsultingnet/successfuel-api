from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Reglement as ReglementModel, Creance as CreanceModel, Avoir as AvoirModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

# Reglement endpoints
@router.get("/reglements", response_model=List[schemas.ReglementCreate])
async def get_reglements(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    reglements = db.query(ReglementModel).offset(skip).limit(limit).all()
    return reglements

@router.post("/reglements", response_model=schemas.ReglementCreate)
async def create_reglement(
    reglement: schemas.ReglementCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_reglement = ReglementModel(**reglement.dict())
    
    db.add(db_reglement)
    db.commit()
    db.refresh(db_reglement)
    
    return db_reglement

@router.get("/reglements/{reglement_id}", response_model=schemas.ReglementCreate)
async def get_reglement_by_id(
    reglement_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    reglement = db.query(ReglementModel).filter(ReglementModel.id == reglement_id).first()
    if not reglement:
        raise HTTPException(status_code=404, detail="Reglement not found")
    return reglement

# Creance endpoints
@router.get("/creances", response_model=List[schemas.CreanceCreate])
async def get_creances(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    creances = db.query(CreanceModel).offset(skip).limit(limit).all()
    return creances

@router.post("/creances", response_model=schemas.CreanceCreate)
async def create_creance(
    creance: schemas.CreanceCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_creance = CreanceModel(**creance.dict())
    
    db.add(db_creance)
    db.commit()
    db.refresh(db_creance)
    
    return db_creance

@router.get("/creances/{creance_id}", response_model=schemas.CreanceCreate)
async def get_creance_by_id(
    creance_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    creance = db.query(CreanceModel).filter(CreanceModel.id == creance_id).first()
    if not creance:
        raise HTTPException(status_code=404, detail="Creance not found")
    return creance

# Avoir endpoints
@router.get("/avoirs", response_model=List[schemas.AvoirCreate])
async def get_avoirs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    avoirs = db.query(AvoirModel).offset(skip).limit(limit).all()
    return avoirs

@router.post("/avoirs", response_model=schemas.AvoirCreate)
async def create_avoir(
    avoir: schemas.AvoirCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_avoir = AvoirModel(**avoir.dict())
    
    db.add(db_avoir)
    db.commit()
    db.refresh(db_avoir)
    
    return db_avoir

@router.get("/avoirs/{avoir_id}", response_model=schemas.AvoirCreate)
async def get_avoir_by_id(
    avoir_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    avoir = db.query(AvoirModel).filter(AvoirModel.id == avoir_id).first()
    if not avoir:
        raise HTTPException(status_code=404, detail="Avoir not found")
    return avoir
