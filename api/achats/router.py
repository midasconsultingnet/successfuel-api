from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from . import schemas
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from ..services.achats import (
    get_achats as service_get_achats,
    create_achat as service_create_achat,
    get_achat_by_id as service_get_achat_by_id,
    update_achat as service_update_achat,
    delete_achat as service_delete_achat,
    get_achat_details as service_get_achat_details
)

router = APIRouter()

@router.get("/",
            response_model=List[schemas.AchatResponse],
            summary="Récupérer les achats de produits",
            description="Récupérer la liste des achats de produits avec pagination. Cet endpoint permet de consulter tous les achats effectués dans le module de boutique, avec filtrage possible par utilisateur, station et compagnie. Nécessite la permission 'Module Achats Boutique'. Les utilisateurs n'ont accès qu'aux achats liés à leur station ou compagnie selon leur rôle.",
            tags=["achats"])
async def get_achats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Achats Boutique"))
):
    return service_get_achats(db, skip, limit)

@router.post("/",
             response_model=schemas.AchatResponse,
             summary="Créer un nouvel achat de produits",
             description="Crée un nouvel achat de produits dans le système. Cet endpoint permet d'enregistrer un achat avec ses détails, y compris les produits achetés, les quantités, les prix et les éventuelles remises. Nécessite la permission 'Module Achats Boutique'. L'utilisateur doit appartenir à la même compagnie que la station concernée par l'achat.",
             tags=["achats"])
async def create_achat(
    achat: schemas.AchatCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Achats Boutique"))
):
    return service_create_achat(db, achat)

@router.get("/{achat_id}",
            response_model=schemas.AchatResponse,
            summary="Récupérer un achat de produit par ID",
            description="Récupère les détails d'un achat de produit spécifique par son identifiant. Cet endpoint permet d'obtenir toutes les informations relatives à un achat spécifique, y compris ses détails de produits achetés. Nécessite la permission 'Module Achats Boutique'. L'utilisateur doit avoir accès à la station ou compagnie liée à l'achat.",
            tags=["achats"])
async def get_achat_by_id(
    achat_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Achats Boutique"))
):
    return service_get_achat_by_id(db, achat_id)

@router.put("/{achat_id}",
            response_model=schemas.AchatResponse,
            summary="Mettre à jour un achat de produit",
            description="Met à jour les informations d'un achat de produit existant. Cet endpoint permet de modifier les détails d'un achat, comme le fournisseur, la date, le statut ou le numéro de pièce comptable. Nécessite la permission 'Module Achats Boutique'. L'utilisateur doit avoir accès à la station ou compagnie liée à l'achat et les modifications peuvent affecter les calculs de stock et de trésorerie.",
            tags=["achats"])
async def update_achat(
    achat_id: int,
    achat: schemas.AchatUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Achats Boutique"))
):
    return service_update_achat(db, achat_id, achat)

@router.delete("/{achat_id}",
                summary="Supprimer un achat de produit",
                description="Supprime un achat de produit du système. Cet endpoint effectue une suppression logique de l'achat en mettant à jour son statut. Nécessite la permission 'Module Achats Boutique'. L'utilisateur doit avoir accès à la station ou compagnie liée à l'achat. La suppression peut affecter les calculs de stock et de trésorerie et ne doit être effectuée que si l'achat n'a pas été entièrement traité.",
                tags=["achats"])
async def delete_achat(
    achat_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Achats Boutique"))
):
    return service_delete_achat(db, achat_id)

@router.get("/{achat_id}/details",
            response_model=List[schemas.AchatDetailResponse],
            summary="Récupérer les détails d'un achat",
            description="Récupère les détails d'un achat spécifique, y compris les produits achetés, les quantités, les prix unitaires et les montants. Nécessite la permission 'Module Achats Boutique'. L'utilisateur doit avoir accès à la station ou compagnie liée à l'achat. Ces détails sont essentiels pour la gestion des stocks et les rapprochements comptables.",
            tags=["achats"])
async def get_achat_details(
    achat_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Achats Boutique"))
):
    return service_get_achat_details(db, achat_id, skip, limit)
