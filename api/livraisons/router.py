from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Livraison as LivraisonModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=List[schemas.LivraisonCreate])
async def get_livraisons(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    livraisons = db.query(LivraisonModel).offset(skip).limit(limit).all()
    return livraisons

@router.post("/", response_model=schemas.LivraisonCreate)
async def create_livraison(
    livraison: schemas.LivraisonCreate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Calculate montant_total if prix_unitaire is provided
    montant_total = None
    if livraison.prix_unitaire:
        montant_total = livraison.prix_unitaire * livraison.quantite_livree
    
    # Create the livraison record
    db_livraison = LivraisonModel(
        station_id=livraison.station_id,
        cuve_id=livraison.cuve_id,
        carburant_id=livraison.carburant_id,
        quantite_livree=livraison.quantite_livree,
        date=livraison.date,
        fournisseur_id=livraison.fournisseur_id,
        numero_bl=livraison.numero_bl,
        numero_facture=livraison.numero_facture,
        prix_unitaire=livraison.prix_unitaire,
        montant_total=montant_total,
        jauge_avant=livraison.jauge_avant,
        jauge_apres=livraison.jauge_apres,
        utilisateur_id=livraison.utilisateur_id,
        commentaires=livraison.commentaires,
        compagnie_id=livraison.compagnie_id
    )
    
    db.add(db_livraison)
    db.commit()
    db.refresh(db_livraison)
    
    return db_livraison

@router.get("/{livraison_id}", response_model=schemas.LivraisonCreate)
async def get_livraison_by_id(
    livraison_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    livraison = db.query(LivraisonModel).filter(LivraisonModel.id == livraison_id).first()
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison not found")
    return livraison

@router.put("/{livraison_id}", response_model=schemas.LivraisonUpdate)
async def update_livraison(
    livraison_id: int, 
    livraison: schemas.LivraisonUpdate, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_livraison = db.query(LivraisonModel).filter(LivraisonModel.id == livraison_id).first()
    if not db_livraison:
        raise HTTPException(status_code=404, detail="Livraison not found")
    
    update_data = livraison.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_livraison, field, value)
    
    # Recalculate montant_total if prix_unitaire is updated
    if livraison.prix_unitaire and db_livraison.quantite_livree:
        db_livraison.montant_total = livraison.prix_unitaire * db_livraison.quantite_livree
    
    db.commit()
    db.refresh(db_livraison)
    return db_livraison

@router.delete("/{livraison_id}")
async def delete_livraison(
    livraison_id: int, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    livraison = db.query(LivraisonModel).filter(LivraisonModel.id == livraison_id).first()
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison not found")
    
    db.delete(livraison)
    db.commit()
    return {"message": "Livraison deleted successfully"}

@router.get("/{cuve_id}/historique")
async def get_livraisons_by_cuve(
    cuve_id: str,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    livraisons = db.query(LivraisonModel).filter(LivraisonModel.cuve_id == cuve_id).offset(skip).limit(limit).all()
    return livraisons
