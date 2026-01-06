from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
from uuid import UUID
from ..database import get_db
from ..auth.auth_handler import get_current_user_security
from ..auth.journalisation import log_user_action
from ..rbac_decorators import require_permission
from .schemas import GroupePartenaireCreate, GroupePartenaireUpdate, GroupePartenaireResponse
from .services.groupe_partenaire_service import GroupePartenaireService


router = APIRouter()


def make_serializable(obj):
    """Convert non-serializable objects to serializable types"""
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        return obj


@router.post(
    "/",
    response_model=GroupePartenaireResponse,
    summary="Créer un nouveau groupe partenaire",
    description="Crée un nouveau groupe partenaire avec les informations fournies.",
    tags=["Groupes Partenaires"],
    dependencies=[Depends(require_permission("Module Groupes Partenaires"))]
)
async def create_groupe_partenaire(
    groupe: GroupePartenaireCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_security)
):
    # Créer le service
    groupe_partenaire_service = GroupePartenaireService()
    # Créer le groupe partenaire
    db_groupe = groupe_partenaire_service.create_groupe_partenaire(db, groupe)

    # Journaliser l'action
    groupe_dict = {k: make_serializable(v) for k, v in db_groupe.__dict__.items() if not k.startswith('_')}
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="groupe_partenaire",
        donnees_apres=groupe_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_groupe


@router.get(
    "/",
    response_model=List[GroupePartenaireResponse],
    summary="Récupérer la liste des groupes partenaires",
    description="Récupère la liste paginée de tous les groupes partenaires.",
    tags=["Groupes Partenaires"],
    dependencies=[Depends(require_permission("Module Groupes Partenaires"))]
)
async def get_groupes_partenaire(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_security)
):
    # Créer le service
    groupe_partenaire_service = GroupePartenaireService()
    # Récupérer les groupes partenaires
    groupes = groupe_partenaire_service.get_groupes_partenaire(db, skip=skip, limit=limit)
    return groupes


@router.get(
    "/{groupe_id}",
    response_model=GroupePartenaireResponse,
    summary="Récupérer un groupe partenaire par son ID",
    description="Récupère les détails d'un groupe partenaire spécifique par son identifiant.",
    tags=["Groupes Partenaires"],
    dependencies=[Depends(require_permission("Module Groupes Partenaires"))]
)
async def get_groupe_partenaire_by_id(
    groupe_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_security)
):
    # Créer le service
    groupe_partenaire_service = GroupePartenaireService()
    # Récupérer le groupe partenaire
    groupe = groupe_partenaire_service.get_groupe_partenaire(db, groupe_id)
    if not groupe:
        raise HTTPException(status_code=404, detail="Groupe partenaire non trouvé")

    return groupe


@router.put(
    "/{groupe_id}",
    response_model=GroupePartenaireResponse,
    summary="Mettre à jour un groupe partenaire",
    description="Met à jour les informations d'un groupe partenaire existant.",
    tags=["Groupes Partenaires"],
    dependencies=[Depends(require_permission("Module Groupes Partenaires"))]
)
async def update_groupe_partenaire(
    groupe_id: str,
    groupe: GroupePartenaireUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_security)
):
    # Créer le service
    groupe_partenaire_service = GroupePartenaireService()
    # Récupérer le groupe partenaire existant
    existing_groupe = groupe_partenaire_service.get_groupe_partenaire(db, groupe_id)
    if not existing_groupe:
        raise HTTPException(status_code=404, detail="Groupe partenaire non trouvé")

    # Journaliser l'action avant la mise à jour
    groupe_dict_before = {k: make_serializable(v) for k, v in existing_groupe.__dict__.items() if not k.startswith('_')}
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="groupe_partenaire",
        donnees_avant=groupe_dict_before,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Mettre à jour le groupe partenaire
    updated_groupe = groupe_partenaire_service.update_groupe_partenaire(db, groupe_id, groupe)
    if not updated_groupe:
        raise HTTPException(status_code=404, detail="Groupe partenaire non trouvé")

    return updated_groupe


@router.delete(
    "/{groupe_id}",
    summary="Supprimer un groupe partenaire",
    description="Supprime un groupe partenaire (suppression douce).",
    tags=["Groupes Partenaires"],
    dependencies=[Depends(require_permission("Module Groupes Partenaires"))]
)
async def delete_groupe_partenaire(
    groupe_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_security)
):
    # Créer le service
    groupe_partenaire_service = GroupePartenaireService()
    # Récupérer le groupe partenaire existant
    existing_groupe = groupe_partenaire_service.get_groupe_partenaire(db, groupe_id)
    if not existing_groupe:
        raise HTTPException(status_code=404, detail="Groupe partenaire non trouvé")

    # Journaliser l'action avant la suppression
    groupe_dict = {k: make_serializable(v) for k, v in existing_groupe.__dict__.items() if not k.startswith('_')}
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="groupe_partenaire",
        donnees_avant=groupe_dict,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Supprimer le groupe partenaire (soft delete)
    success = groupe_partenaire_service.delete_groupe_partenaire(db, groupe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Groupe partenaire non trouvé")

    return {"message": "Groupe partenaire supprimé avec succès"}