from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..auth.auth_handler import get_current_user_security
from ..auth.schemas import UserWithPermissions
from ..rbac_decorators import require_permission
from ..services.achats.demande_achat_service import DemandeAchatService
from .demande_achat_schemas import (
    DemandeAchatCreate,
    DemandeAchatUpdate,
    DemandeAchatResponse,
    LigneDemandeAchatCreate,
    LigneDemandeAchatResponse
)

router = APIRouter(prefix="/achats", tags=["Achats"])

@router.post("/demandes-achat/", response_model=DemandeAchatResponse)
def create_demande_achat(
    demande: DemandeAchatCreate,
    current_user: UserWithPermissions = Depends(require_permission("achats", "create")),
    db: Session = Depends(get_db)
):
    service = DemandeAchatService(db)
    try:
        result = service.create_demande_achat(current_user.id, demande.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/demandes-achat/{demande_id}", response_model=DemandeAchatResponse)
def get_demande_achat(
    demande_id: UUID,
    current_user: UserWithPermissions = Depends(require_permission("achats", "read")),
    db: Session = Depends(get_db)
):
    service = DemandeAchatService(db)
    try:
        result = service.get_demande_achat_with_details(demande_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/demandes-achat/{demande_id}", response_model=DemandeAchatResponse)
def update_demande_achat(
    demande_id: UUID,
    demande_update: DemandeAchatUpdate,
    current_user: UserWithPermissions = Depends(require_permission("achats", "update")),
    db: Session = Depends(get_db)
):
    service = DemandeAchatService(db)
    try:
        result = service.update_demande_achat(demande_id, demande_update.dict(exclude_unset=True))
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/demandes-achat/{demande_id}/valider")
def valider_demande_achat(
    demande_id: UUID,
    current_user: UserWithPermissions = Depends(require_permission("achats", "update")),
    db: Session = Depends(get_db)
):
    service = DemandeAchatService(db)
    try:
        result = service.valider_demande_achat(demande_id, current_user.id)
        return {"status": "success", "message": "Demande d'achat validée avec succès", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/demandes-achat/{demande_id}/rejeter")
def rejeter_demande_achat(
    demande_id: UUID,
    current_user: UserWithPermissions = Depends(require_permission("achats", "update")),
    db: Session = Depends(get_db)
):
    service = DemandeAchatService(db)
    try:
        result = service.rejeter_demande_achat(demande_id, current_user.id)
        return {"status": "success", "message": "Demande d'achat rejetée avec succès", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))