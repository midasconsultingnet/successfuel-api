from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Reglement as ReglementModel, Creance as CreanceModel, Avoir as AvoirModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..rbac_decorators import require_permission
from ..auth.auth_handler import get_current_user_security

router = APIRouter()
security = HTTPBearer()

# Reglement endpoints
@router.get("/reglements", response_model=List[schemas.ReglementCreate],
           summary="Récupérer la liste des règlements",
           description="Permet de récupérer la liste des règlements appartenant à la compagnie de l'utilisateur connecté")
async def get_reglements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    reglements = db.query(ReglementModel).filter(
        ReglementModel.compagnie_id == str(current_user.compagnie_id)
    ).offset(skip).limit(limit).all()
    return reglements

@router.post("/reglements", response_model=schemas.ReglementCreate,
            summary="Créer un nouveau règlement",
            description="Permet de créer un nouveau règlement pour la compagnie de l'utilisateur connecté")
async def create_reglement(
    reglement: schemas.ReglementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    # Vérifier que l'utilisateur appartient à la même compagnie que le reglement
    if reglement.dict().get('compagnie_id') != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : appartenance à la compagnie requise")

    db_reglement = ReglementModel(**reglement.dict())
    db_reglement.compagnie_id = str(current_user.compagnie_id)  # S'assurer que le bon ID compagnie est assigné

    db.add(db_reglement)
    db.commit()
    db.refresh(db_reglement)

    return db_reglement

@router.get("/reglements/{reglement_id}", response_model=schemas.ReglementCreate,
           summary="Récupérer un règlement par son ID",
           description="Permet de récupérer les détails d'un règlement spécifique par son identifiant")
async def get_reglement_by_id(
    reglement_id: str,  # Changement de int à str pour UUID
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    reglement = db.query(ReglementModel).filter(
        ReglementModel.id == reglement_id,
        ReglementModel.compagnie_id == str(current_user.compagnie_id)
    ).first()
    if not reglement:
        raise HTTPException(status_code=404, detail="Reglement not found")
    return reglement

# Creance endpoints
@router.get("/creances", response_model=List[schemas.CreanceCreate],
           summary="Récupérer la liste des créances",
           description="Permet de récupérer la liste des créances appartenant à la compagnie de l'utilisateur connecté")
async def get_creances(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    creances = db.query(CreanceModel).filter(
        CreanceModel.compagnie_id == str(current_user.compagnie_id)
    ).offset(skip).limit(limit).all()
    return creances

@router.post("/creances", response_model=schemas.CreanceCreate,
            summary="Créer une nouvelle créance",
            description="Permet de créer une nouvelle créance pour la compagnie de l'utilisateur connecté")
async def create_creance(
    creance: schemas.CreanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    # Vérifier que l'utilisateur appartient à la même compagnie que la créance
    if creance.dict().get('compagnie_id') != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : appartenance à la compagnie requise")

    db_creance = CreanceModel(**creance.dict())
    db_creance.compagnie_id = str(current_user.compagnie_id)  # S'assurer que le bon ID compagnie est assigné

    db.add(db_creance)
    db.commit()
    db.refresh(db_creance)

    return db_creance

@router.get("/creances/{creance_id}", response_model=schemas.CreanceCreate,
           summary="Récupérer une créance par son ID",
           description="Permet de récupérer les détails d'une créance spécifique par son identifiant")
async def get_creance_by_id(
    creance_id: str,  # Changement de int à str pour UUID
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    creance = db.query(CreanceModel).filter(
        CreanceModel.id == creance_id,
        CreanceModel.compagnie_id == str(current_user.compagnie_id)
    ).first()
    if not creance:
        raise HTTPException(status_code=404, detail="Creance not found")
    return creance

# Avoir endpoints
@router.get("/avoirs", response_model=List[schemas.AvoirCreate],
           summary="Récupérer la liste des avoirs",
           description="Permet de récupérer la liste des avoirs appartenant à la compagnie de l'utilisateur connecté")
async def get_avoirs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    avoirs = db.query(AvoirModel).filter(
        AvoirModel.compagnie_id == str(current_user.compagnie_id)
    ).offset(skip).limit(limit).all()
    return avoirs

@router.post("/avoirs", response_model=schemas.AvoirCreate,
            summary="Créer un nouvel avoir",
            description="Permet de créer un nouvel avoir pour la compagnie de l'utilisateur connecté")
async def create_avoir(
    avoir: schemas.AvoirCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    # Vérifier que l'utilisateur appartient à la même compagnie que l'avoir
    if avoir.dict().get('compagnie_id') != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé : appartenance à la compagnie requise")

    # Calcul du montant restant
    montant_restant = avoir.montant_initial - avoir.montant_utilise
    avoir_dict = avoir.dict()
    avoir_dict['montant_restant'] = montant_restant
    avoir_dict['compagnie_id'] = str(current_user.compagnie_id)  # S'assurer que le bon ID compagnie est assigné

    db_avoir = AvoirModel(**avoir_dict)

    db.add(db_avoir)
    db.commit()
    db.refresh(db_avoir)

    return db_avoir

@router.get("/avoirs/{avoir_id}", response_model=schemas.AvoirCreate,
           summary="Récupérer un avoir par son ID",
           description="Permet de récupérer les détails d'un avoir spécifique par son identifiant")
async def get_avoir_by_id(
    avoir_id: str,  # Changement de int à str pour UUID
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    avoir = db.query(AvoirModel).filter(
        AvoirModel.id == avoir_id,
        AvoirModel.compagnie_id == str(current_user.compagnie_id)
    ).first()
    if not avoir:
        raise HTTPException(status_code=404, detail="Avoir not found")
    return avoir

@router.put("/avoirs/{avoir_id}", response_model=schemas.AvoirCreate,
           summary="Mettre à jour un avoir",
           description="Permet de modifier les informations d'un avoir existant")
async def update_avoir(
    avoir_id: str,  # Changement de int à str pour UUID
    avoir: schemas.AvoirUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Mouvements Financiers"))
):
    db_avoir = db.query(AvoirModel).filter(
        AvoirModel.id == avoir_id,
        AvoirModel.compagnie_id == str(current_user.compagnie_id)
    ).first()
    if not db_avoir:
        raise HTTPException(status_code=404, detail="Avoir not found")

    # Mise à jour des champs
    update_data = avoir.dict(exclude_unset=True)

    # Si le montant_utilise est mis à jour, recalcul du montant_restant
    if 'montant_utilise' in update_data:
        montant_restant = db_avoir.montant_initial - update_data['montant_utilise']
        update_data['montant_restant'] = montant_restant

        # Mise à jour du statut en fonction du montant utilisé
        if update_data['montant_utilise'] == 0:
            update_data['statut'] = 'emis'
        elif update_data['montant_utilise'] >= db_avoir.montant_initial:
            update_data['statut'] = 'utilise'
        else:
            update_data['statut'] = 'partiellement_utilise'

    # Mise à jour des champs
    for field, value in update_data.items():
        setattr(db_avoir, field, value)

    db.commit()
    db.refresh(db_avoir)
    return db_avoir
