from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from . import schemas
from api.services.comptabilite.ecriture_comptable_service import EcritureComptableService
import uuid
from datetime import datetime

router = APIRouter(tags=["Ecriture comptable"])

@router.get("/", response_model=List[schemas.EcritureComptableResponse],
           summary="Récupérer la liste des écritures comptables",
           dependencies=[Depends(require_permission("ecritures_comptables"))])
async def get_ecritures_comptables(
    skip: int = 0,
    limit: int = 100,
    date_debut: str = None,
    date_fin: str = None,
    compagnie_id: str = None,
    est_validee: bool = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    service = EcritureComptableService()
    
    # Construire les filtres
    filters = {}
    if date_debut:
        filters['date_debut'] = datetime.strptime(date_debut, "%Y-%m-%d")
    if date_fin:
        filters['date_fin'] = datetime.strptime(date_fin, "%Y-%m-%d")
    if compagnie_id:
        filters['compagnie_id'] = uuid.UUID(compagnie_id)
    else:
        filters['compagnie_id'] = current_user.compagnie_id
    if est_validee is not None:
        filters['est_validee'] = est_validee
    
    # Récupérer les écritures avec les filtres
    ecritures = service.get_all_with_filters(db, skip, limit, **filters)
    return ecritures

@router.post("/", response_model=schemas.EcritureComptableResponse,
             summary="Créer une nouvelle écriture comptable",
             dependencies=[Depends(require_permission("ecritures_comptables"))])
async def create_ecriture_comptable(
    ecriture: schemas.EcritureComptableCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    service = EcritureComptableService()
    ecriture_data = ecriture.dict()
    ecriture_data['utilisateur_id'] = current_user.id
    ecriture_data['compagnie_id'] = current_user.compagnie_id
    return service.creer_ecriture(ecriture_data, db)

@router.put("/{ecriture_id}/valider",
            summary="Valider une écriture comptable",
            dependencies=[Depends(require_permission("ecritures_comptables"))])
async def valider_ecriture_comptable(
    ecriture_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    service = EcritureComptableService()
    try:
        ecriture_uuid = uuid.UUID(ecriture_id)
        return service.valider_ecriture(ecriture_uuid, db)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'écriture invalide")

@router.get("/{ecriture_id}", response_model=schemas.EcritureComptableResponse,
           summary="Récupérer une écriture comptable par son ID",
           dependencies=[Depends(require_permission("ecritures_comptables"))])
async def get_ecriture_comptable_by_id(
    ecriture_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    service = EcritureComptableService()
    try:
        ecriture_uuid = uuid.UUID(ecriture_id)
        ecriture = service.get_by_id(ecriture_uuid, db)
        if not ecriture:
            raise HTTPException(status_code=404, detail="Écriture non trouvée")
        return ecriture
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'écriture invalide")