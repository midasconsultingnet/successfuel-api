from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from ..plan_comptable.schemas import (
    PlanComptableCreate,
    PlanComptableUpdate,
    PlanComptableResponse,
    PlanComptableHierarchyResponse
)
from ..services.plan_comptable.plan_comptable_service import PlanComptableService

router = APIRouter(prefix="/plan-comptable", tags=["Plan Comptable"])

@require_permission("plan_comptable:create")
@router.post("/", response_model=PlanComptableResponse, status_code=status.HTTP_201_CREATED)
async def create_plan_comptable(
    plan: PlanComptableCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Créer un nouveau compte dans le plan comptable
    """
    service = PlanComptableService(db)
    try:
        return service.create_plan_comptable(plan)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@require_permission("plan_comptable:read")
@router.get("/{plan_id}", response_model=PlanComptableResponse)
async def get_plan_comptable(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Récupérer un compte par son ID
    """
    service = PlanComptableService(db)
    plan = service.get_plan_comptable(plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    return plan

@require_permission("plan_comptable:update")
@router.put("/{plan_id}", response_model=PlanComptableResponse)
async def update_plan_comptable(
    plan_id: UUID,
    plan: PlanComptableUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Mettre à jour un compte existant
    """
    service = PlanComptableService(db)
    updated_plan = service.update_plan_comptable(plan_id, plan)
    if not updated_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    return updated_plan

@require_permission("plan_comptable:delete")
@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan_comptable(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Supprimer (soft delete) un compte
    """
    service = PlanComptableService(db)
    deleted = service.delete_plan_comptable(plan_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    return

@require_permission("plan_comptable:read")
@router.get("/", response_model=List[PlanComptableResponse])
async def get_all_plans_comptables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Récupérer tous les comptes avec pagination
    """
    service = PlanComptableService(db)
    return service.get_all_plans_comptables(skip=skip, limit=limit)

@require_permission("plan_comptable:read")
@router.get("/{plan_id}/hierarchy", response_model=PlanComptableHierarchyResponse)
async def get_plan_hierarchy(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Récupérer un compte avec sa hiérarchie complète
    """
    service = PlanComptableService(db)
    plan = service.get_plan_hierarchy(plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    return plan

@require_permission("plan_comptable:read")
@router.get("/hierarchy/full", response_model=List[PlanComptableHierarchyResponse])
async def get_full_plan_hierarchy(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Récupérer la hiérarchie complète du plan comptable
    """
    service = PlanComptableService(db)
    return service.get_full_plan_hierarchy(current_user.compagnie_id)

@require_permission("plan_comptable:read")
@router.get("/by-numero/{numero_compte}", response_model=PlanComptableHierarchyResponse)
async def get_plan_hierarchy_by_numero(
    numero_compte: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_security)
):
    """
    Récupérer un compte avec sa hiérarchie complète par son numéro de compte
    """
    service = PlanComptableService(db)
    plan = service.get_plan_hierarchy_by_numero(numero_compte, current_user.compagnie_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte non trouvé")
    return plan