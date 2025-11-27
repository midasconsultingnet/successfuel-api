from datetime import timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from models.structures import Utilisateur, Profil, ProfilPermission, Permission, Module, Compagnie, Station
from models.securite import EvenementSecurite, ModificationSensible
from services.auth_service import authenticate_user, create_user, get_user_by_id, update_user, delete_user, activate_user, deactivate_user, log_login_attempt
from services.rbac_service import create_profil, get_profil_by_id, update_profil, delete_profil, get_all_profils, get_all_permissions, get_all_modules, create_permission, create_module, get_permissions_for_profil, assign_permissions_to_profil, get_permission_by_id, get_module_by_id, check_user_permission, get_user_profil, get_permissions_for_user
from services.journalisation_service import JournalisationService
from utils.security import verify_token
from utils.dependencies import get_current_user
from utils.access_control import require_permission

router = APIRouter(
    tags=["securite"],
    responses={404: {"description": "Endpoint non trouvé"}}
)

class ProfileCreate(BaseModel):
    code: str
    libelle: str
    description: Optional[str] = None
    permission_ids: List[str] = []

class ProfileUpdate(BaseModel):
    libelle: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    permission_ids: List[str] = []

class ModuleCreate(BaseModel):
    libelle: str
    statut: Optional[str] = "Actif"

class PermissionCreate(BaseModel):
    libelle: str
    module_id: str
    description: Optional[str] = None
    statut: Optional[str] = "Actif"


@router.post("/login")
def login(
    request: Request,
    login: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et génère un jeton JWT
    """
    ip_connexion = request.client.host

    # Utiliser la fonction d'authentification utilisateur existante
    result = authenticate_user(db, login, password)
    if not result:
        # Enregistrer une tentative de connexion échouée
        JournalisationService.log_failed_login_attempt(
            db,
            login,
            ip_connexion=ip_connexion
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects"
        )

    # Enregistrer une tentative de connexion réussie
    JournalisationService.log_successful_login(
        db,
        login,
        str(result["user"].id),
        ip_connexion=ip_connexion
    )

    return {
        "success": True,
        "data": result,
        "message": "Connexion réussie"
    }


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Déconnecte l'utilisateur en invalidant le jeton
    """
    # Note: Cette implémentation suppose que le token est passé dans la requête
    # En pratique, vous devez extraire le token des en-têtes pour l'invalider
    # Pour l'instant, nous retournons simplement un message de succès
    return {
        "success": True,
        "message": "Déconnexion réussie"
    }


@router.get("/profiles")
def get_profiles(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
):
    """
    Récupère tous les profils avec leurs permissions
    """
    # Vérifier si l'utilisateur a la permission de gérer les profils
    has_permission = check_user_permission(db, str(current_user.id), "lire_profils")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour accéder aux profils"
        )

    profils = get_all_profils(db)
    
    # Filtrer si nécessaire
    if search:
        profils = [p for p in profils if search.lower() in p.libelle.lower()]

    # Appliquer pagination
    start = skip
    end = skip + limit
    profiles = profils[start:end]
    
    # Compter le total pour la pagination
    total = len(profils)

    # Récupérer les permissions pour chaque profil
    profile_data = []
    for profile in profiles:
        permissions = get_permissions_for_profil(db, str(profile.id))

        profile_data.append({
            "id": str(profile.id),
            "code": profile.code,
            "libelle": profile.libelle,
            "description": profile.description,
            "statut": profile.statut,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            "permissions": [
                {
                    "id": str(perm.id),
                    "libelle": perm.libelle,
                    "description": perm.description,
                }
                for perm in permissions
            ]
        })

    return {
        "success": True,
        "data": {
            "profiles": profile_data,
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Profils récupérés avec succès"
    }


@router.post("/profiles")
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Crée un nouveau profil avec ses permissions
    """
    # Vérifier si l'utilisateur a la permission de créer des profils
    has_permission = check_user_permission(db, str(current_user.id), "creer_profils")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour créer des profils"
        )

    # Créer le profil avec ses permissions
    try:
        nouveau_profil = create_profil(
            db,
            code=profile_data.code,
            libelle=profile_data.libelle,
            description=profile_data.description,
            compagnie_id=str(current_user.compagnie_id) if current_user.compagnie_id else None
        )

        # Assigner les permissions
        if profile_data.permission_ids:
            assign_permissions_to_profil(db, str(nouveau_profil.id), profile_data.permission_ids)

        # Enregistrer l'événement de sécurité
        JournalisationService.log_security_event(
            db,
            type_evenement="creation_profil",
            description=f"Profil '{nouveau_profil.libelle}' créé par '{current_user.login}'",
            utilisateur_id=str(current_user.id)
        )

        return {
            "success": True,
            "data": {
                "id": str(nouveau_profil.id),
                "code": nouveau_profil.code,
                "libelle": nouveau_profil.libelle,
                "description": nouveau_profil.description,
                "statut": nouveau_profil.statut,
                "created_at": nouveau_profil.created_at,
                "updated_at": nouveau_profil.updated_at,
            },
            "message": "Profil créé avec succès"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du profil: {str(e)}"
        )


@router.put("/profiles/{profile_id}")
def update_profile(
    profile_id: str,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Met à jour un profil avec ses permissions
    """
    # Vérifier si l'utilisateur a la permission de modifier des profils
    has_permission = check_user_permission(db, str(current_user.id), "modifier_profils")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour modifier des profils"
        )

    # Récupérer le profil
    profil = get_profil_by_id(db, profile_id)
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil non trouvé"
        )

    # Mettre à jour les champs
    update_data = {}
    if profile_data.libelle is not None:
        update_data['libelle'] = profile_data.libelle
    if profile_data.description is not None:
        update_data['description'] = profile_data.description
    if profile_data.statut is not None:
        update_data['statut'] = profile_data.statut

    updated_profil = update_profil(db, profile_id, **update_data)

    # Mettre à jour les permissions si elles sont spécifiées
    if profile_data.permission_ids:
        assign_permissions_to_profil(db, profile_id, profile_data.permission_ids)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="modification_profil",
        description=f"Profil '{updated_profil.libelle}' modifié par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(updated_profil.id),
            "code": updated_profil.code,
            "libelle": updated_profil.libelle,
            "description": updated_profil.description,
            "statut": updated_profil.statut,
            "created_at": updated_profil.created_at,
            "updated_at": updated_profil.updated_at,
        },
        "message": "Profil mis à jour avec succès"
    }