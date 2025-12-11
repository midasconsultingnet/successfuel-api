from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Charge as ChargeModel, CategorieCharge as CategorieChargeModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

# Categorie Charge endpoints
@router.get("/categories", response_model=List[schemas.CategorieChargeCreate])
async def get_categories_charges(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    categories = db.query(CategorieChargeModel).offset(skip).limit(limit).all()
    return categories

@router.post("/categories", response_model=schemas.CategorieChargeCreate)
async def create_categorie_charge(
    categorie: schemas.CategorieChargeCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Check if category already exists in the company
    db_categorie = db.query(CategorieChargeModel).filter(
        CategorieChargeModel.nom == categorie.nom,
        CategorieChargeModel.compagnie_id == categorie.compagnie_id
    ).first()
    if db_categorie:
        raise HTTPException(status_code=400, detail="Category with this name already exists for this company")
    
    db_categorie = CategorieChargeModel(**categorie.dict())
    
    db.add(db_categorie)
    db.commit()
    db.refresh(db_categorie)
    
    return db_categorie

# Charge endpoints
@router.get("/", response_model=List[schemas.ChargeCreate])
async def get_charges(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    charges = db.query(ChargeModel).offset(skip).limit(limit).all()
    return charges

@router.post("/", response_model=schemas.ChargeCreate)
async def create_charge(
    charge: schemas.ChargeCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_charge = ChargeModel(**charge.dict())
    
    db.add(db_charge)
    db.commit()
    db.refresh(db_charge)
    
    return db_charge

@router.get("/{charge_id}", response_model=schemas.ChargeCreate)
async def get_charge_by_id(
    charge_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    charge = db.query(ChargeModel).filter(ChargeModel.id == charge_id).first()
    if not charge:
        raise HTTPException(status_code=404, detail="Charge not found")
    return charge

@router.put("/{charge_id}", response_model=schemas.ChargeUpdate)
async def update_charge(
    charge_id: int, 
    charge: schemas.ChargeUpdate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_charge = db.query(ChargeModel).filter(ChargeModel.id == charge_id).first()
    if not db_charge:
        raise HTTPException(status_code=404, detail="Charge not found")
    
    update_data = charge.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_charge, field, value)
    
    db.commit()
    db.refresh(db_charge)
    return db_charge

@router.delete("/{charge_id}")
async def delete_charge(
    charge_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    charge = db.query(ChargeModel).filter(ChargeModel.id == charge_id).first()
    if not charge:
        raise HTTPException(status_code=404, detail="Charge not found")
    
    db.delete(charge)
    db.commit()
    return {"message": "Charge deleted successfully"}

@router.get("/categorie/{categorie}")
async def get_charges_by_categorie(
    categorie: str,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    charges = db.query(ChargeModel).filter(ChargeModel.categorie == categorie).offset(skip).limit(limit).all()
    return charges
