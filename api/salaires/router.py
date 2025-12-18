from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Salaire as SalaireModel, Prime as PrimeModel, Avance as AvanceModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(tags=["Salaires"])
security = HTTPBearer()

# Salaire endpoints
@router.get("/", response_model=List[schemas.SalaireResponse],
           summary="Récupérer la liste des salaires",
           description="Permet de récupérer la liste des salaires avec possibilité de pagination")
async def get_salaires(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    salaires = db.query(SalaireModel).offset(skip).limit(limit).all()
    return salaires

@router.post("/", response_model=schemas.SalaireResponse,
             summary="Créer un nouveau salaire",
             description="Permet de créer une nouvelle fiche de salaire pour un employé")
async def create_salaire(
    salaire: schemas.SalaireCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_salaire = SalaireModel(**salaire.dict())
    
    db.add(db_salaire)
    db.commit()
    db.refresh(db_salaire)
    
    return db_salaire

@router.get("/{salaire_id}", response_model=schemas.SalaireResponse,
           summary="Récupérer un salaire par son ID",
           description="Permet de récupérer les détails d'un salaire spécifique par son identifiant")
async def get_salaire_by_id(
    salaire_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    salaire = db.query(SalaireModel).filter(SalaireModel.id == salaire_id).first()
    if not salaire:
        raise HTTPException(status_code=404, detail="Salaire not found")
    return salaire

@router.put("/{salaire_id}", response_model=schemas.SalaireResponse,
           summary="Mettre à jour un salaire",
           description="Permet de modifier les informations d'un salaire existant")
async def update_salaire(
    salaire_id: int,
    salaire: schemas.SalaireUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_salaire = db.query(SalaireModel).filter(SalaireModel.id == salaire_id).first()
    if not db_salaire:
        raise HTTPException(status_code=404, detail="Salaire not found")
    
    update_data = salaire.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_salaire, field, value)
    
    db.commit()
    db.refresh(db_salaire)
    return db_salaire

@router.delete("/{salaire_id}",
               summary="Supprimer un salaire",
               description="Permet de supprimer un salaire existant")
async def delete_salaire(
    salaire_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    salaire = db.query(SalaireModel).filter(SalaireModel.id == salaire_id).first()
    if not salaire:
        raise HTTPException(status_code=404, detail="Salaire not found")
    
    db.delete(salaire)
    db.commit()
    return {"message": "Salaire deleted successfully"}

@router.get("/{employe_id}/historique",
           summary="Récupérer l'historique des salaires d'un employé",
           description="Permet de récupérer l'historique des salaires d'un employé spécifique")
async def get_salaire_historique(
    employe_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    salaires = db.query(SalaireModel).filter(SalaireModel.employe_id == employe_id).offset(skip).limit(limit).all()
    return salaires

# Prime endpoints
@router.get("/primes", response_model=List[schemas.PrimeResponse],
           summary="Récupérer la liste des primes",
           description="Permet de récupérer la liste des primes avec possibilité de pagination")
async def get_primes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    primes = db.query(PrimeModel).offset(skip).limit(limit).all()
    return primes

@router.post("/primes", response_model=schemas.PrimeResponse,
             summary="Créer une nouvelle prime",
             description="Permet de créer une nouvelle prime pour un employé")
async def create_prime(
    prime: schemas.PrimeCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_prime = PrimeModel(**prime.dict())
    
    db.add(db_prime)
    db.commit()
    db.refresh(db_prime)
    
    return db_prime

# Avance endpoints
@router.get("/avances", response_model=List[schemas.AvanceResponse],
           summary="Récupérer la liste des avances",
           description="Permet de récupérer la liste des avances avec possibilité de pagination")
async def get_avances(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    avances = db.query(AvanceModel).offset(skip).limit(limit).all()
    return avances

@router.post("/avances", response_model=schemas.AvanceResponse,
             summary="Créer une nouvelle avance",
             description="Permet de créer une nouvelle avance pour un employé")
async def create_avance(
    avance: schemas.AvanceCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_avance = AvanceModel(**avance.dict())
    
    db.add(db_avance)
    db.commit()
    db.refresh(db_avance)
    
    return db_avance
