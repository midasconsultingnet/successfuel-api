from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Tresorerie as TresorerieModel, Transfert as TransfertModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

# Tresorerie endpoints
@router.get("/", response_model=List[schemas.TresorerieCreate])
async def get_tresoreries(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    tresoreries = db.query(TresorerieModel).offset(skip).limit(limit).all()
    return tresoreries

@router.post("/", response_model=schemas.TresorerieCreate)
async def create_tresorerie(
    tresorerie: schemas.TresorerieCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Check if tresorerie already exists
    db_tresorerie = db.query(TresorerieModel).filter(
        TresorerieModel.nom == tresorerie.nom,
        TresorerieModel.type == tresorerie.type,
        TresorerieModel.station_id == tresorerie.station_id
    ).first()
    if db_tresorerie:
        raise HTTPException(status_code=400, detail="Tresorerie with this name and type already exists for this station")
    
    db_tresorerie = TresorerieModel(**tresorerie.dict())
    db.add(db_tresorerie)
    db.commit()
    db.refresh(db_tresorerie)
    
    return db_tresorerie

@router.get("/{tresorerie_id}", response_model=schemas.TresorerieCreate)
async def get_tresorerie_by_id(
    tresorerie_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    tresorerie = db.query(TresorerieModel).filter(TresorerieModel.id == tresorerie_id).first()
    if not tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")
    return tresorerie

@router.put("/{tresorerie_id}", response_model=schemas.TresorerieUpdate)
async def update_tresorerie(
    tresorerie_id: int, 
    tresorerie: schemas.TresorerieUpdate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_tresorerie = db.query(TresorerieModel).filter(TresorerieModel.id == tresorerie_id).first()
    if not db_tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")
    
    update_data = tresorerie.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tresorerie, field, value)
    
    db.commit()
    db.refresh(db_tresorerie)
    return db_tresorerie

@router.delete("/{tresorerie_id}")
async def delete_tresorerie(
    tresorerie_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    tresorerie = db.query(TresorerieModel).filter(TresorerieModel.id == tresorerie_id).first()
    if not tresorerie:
        raise HTTPException(status_code=404, detail="Tresorerie not found")
    
    db.delete(tresorerie)
    db.commit()
    return {"message": "Tresorerie deleted successfully"}

# Transfert endpoints
@router.post("/transferts", response_model=schemas.TransfertCreate)
async def create_transfert(
    transfert: schemas.TransfertCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify that both treasury accounts exist and have sufficient balance
    source_tresorerie = db.query(TresorerieModel).filter(TresorerieModel.id == int(transfert.tresorerie_source_id)).first()
    if not source_tresorerie:
        raise HTTPException(status_code=404, detail="Source tresorerie not found")
    
    if source_tresorerie.solde < transfert.montant:
        raise HTTPException(status_code=400, detail="Insufficient balance in source tresorerie")
    
    destination_tresorerie = db.query(TresorerieModel).filter(TresorerieModel.id == int(transfert.tresorerie_destination_id)).first()
    if not destination_tresorerie:
        raise HTTPException(status_code=404, detail="Destination tresorerie not found")
    
    # Create the transfert record
    db_transfert = TransfertModel(**transfert.dict())
    
    # Update the treasury balances
    source_tresorerie.solde -= transfert.montant
    destination_tresorerie.solde += transfert.montant
    
    db.add(db_transfert)
    db.commit()
    db.refresh(db_transfert)
    
    return db_transfert

@router.get("/transferts", response_model=List[schemas.TransfertCreate])
async def get_transferts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    transferts = db.query(TransfertModel).offset(skip).limit(limit).all()
    return transferts
