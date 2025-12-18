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

router = APIRouter(prefix="/achats", tags=["achats"])

@router.post("/demandes-achat/",
             response_model=DemandeAchatResponse,
             summary="Créer une nouvelle demande d'achat",
             description="Crée une nouvelle demande d'achat dans le système. Cette fonctionnalité permet aux employés de demander l'approvisionnement en produits ou en marchandises. Nécessite la permission 'achats' avec droit de création.",
             tags=["achats"])
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


@router.get("/demandes-achat/{demande_id}",
            response_model=DemandeAchatResponse,
            summary="Récupérer une demande d'achat par ID",
            description="Récupère les détails d'une demande d'achat spécifique par son identifiant. Permet d'obtenir toutes les informations relatives à une demande d'achat, y compris ses lignes de produits demandés et son statut de validation. Nécessite la permission 'achats' avec droit de lecture.",
            tags=["achats"])
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


@router.put("/demandes-achat/{demande_id}",
            response_model=DemandeAchatResponse,
            summary="Mettre à jour une demande d'achat",
            description="Met à jour les informations d'une demande d'achat existante. Permet de modifier les détails de la demande, comme les produits demandés, les quantités ou les commentaires. Nécessite la permission 'achats' avec droit de mise à jour.",
            tags=["achats"])
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


@router.post("/demandes-achat/{demande_id}/valider",
             summary="Valider une demande d'achat",
             description="Valide une demande d'achat existante. Ce processus permet de confirmer la commande et de lancer le processus d'approvisionnement. Nécessite la permission 'achats' avec droit de mise à jour.",
             tags=["achats"])
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


@router.post("/demandes-achat/{demande_id}/rejeter",
             summary="Rejeter une demande d'achat",
             description="Rejette une demande d'achat existante. Ce processus permet d'annuler la commande et d'indiquer qu'elle ne sera pas satisfaite. Nécessite la permission 'achats' avec droit de mise à jour.",
             tags=["achats"])
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