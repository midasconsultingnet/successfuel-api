from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Inventaire as InventaireModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=List[schemas.InventaireCreate])
async def get_inventaires(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    inventaires = db.query(InventaireModel).offset(skip).limit(limit).all()
    return inventaires

@router.post("/", response_model=schemas.InventaireCreate)
async def create_inventaire(
    inventaire: schemas.InventaireCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Create the inventaire record
    db_inventaire = InventaireModel(**inventaire.dict())
    
    db.add(db_inventaire)
    db.commit()
    db.refresh(db_inventaire)
    
    return db_inventaire

@router.get("/{inventaire_id}", response_model=schemas.InventaireCreate)
async def get_inventaire_by_id(
    inventaire_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    inventaire = db.query(InventaireModel).filter(InventaireModel.id == inventaire_id).first()
    if not inventaire:
        raise HTTPException(status_code=404, detail="Inventaire not found")
    return inventaire

@router.put("/{inventaire_id}", response_model=schemas.InventaireUpdate)
async def update_inventaire(
    inventaire_id: int, 
    inventaire: schemas.InventaireUpdate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_inventaire = db.query(InventaireModel).filter(InventaireModel.id == inventaire_id).first()
    if not db_inventaire:
        raise HTTPException(status_code=404, detail="Inventaire not found")
    
    update_data = inventaire.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_inventaire, field, value)
    
    db.commit()
    db.refresh(db_inventaire)
    return db_inventaire

@router.delete("/{inventaire_id}")
async def delete_inventaire(
    inventaire_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    inventaire = db.query(InventaireModel).filter(InventaireModel.id == inventaire_id).first()
    if not inventaire:
        raise HTTPException(status_code=404, detail="Inventaire not found")
    
    db.delete(inventaire)
    db.commit()
    return {"message": "Inventaire deleted successfully"}

@router.get("/{inventaire_id}/ecarts")
async def get_inventaire_ecarts(
    inventaire_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # This endpoint would compute and return the discrepancies between real and theoretical stock
    inventaire = db.query(InventaireModel).filter(InventaireModel.id == inventaire_id).first()
    if not inventaire:
        raise HTTPException(status_code=404, detail="Inventaire not found")
    
    # In a real implementation, this would calculate ecart by comparing 
    # the quantite_reelle with theoretical stock from the stock module
    # For now, returning a placeholder response
    return {
        "inventaire_id": inventaire_id,
        "ecart": inventaire.ecart,
        "type_ecart": inventaire.type_ecart,
        "message": "This endpoint would calculate and return the discrepancies between real and theoretical stock"
    }
