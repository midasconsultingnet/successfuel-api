from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database.database import get_db
from models.structures import Utilisateur
from services.auth_service import (
    authenticate_user, create_user, get_user_by_id, update_user, 
    delete_user, activate_user, deactivate_user, create_refresh_token,
    logout_user, logout_all_user_sessions
)
from services.rbac_service import get_user_profil, get_permissions_for_user
from utils.security import verify_token
from utils.dependencies import get_current_user
from config.config import settings
import uuid


# Create API router
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
    responses={404: {"description": "Endpoint non trouvé"}}
)


# Request/response models
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    login: str
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    profil_id: Optional[str] = None
    compagnie_id: Optional[str] = None
    type_utilisateur: str = "utilisateur_compagnie"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    profil_id: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    stations_user: Optional[List[str]] = None
    statut: Optional[str] = None


class User(UserBase):
    id: str
    statut: str
    last_login: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    login: str
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    success: bool
    data: dict


class UserResponse(BaseModel):
    success: bool
    data: User


class MessageResponse(BaseModel):
    success: bool
    message: str




@router.post("/login", response_model=LoginResponse)
async def login_for_access_token(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token
    """
    # For user login endpoint, always use 'utilisateur' endpoint type
    user_auth_result = authenticate_user(
        db,
        user_credentials.login,
        user_credentials.password,
        endpoint_type="utilisateur"
    )

    if not user_auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_auth_result["user"]

    # Create user response data
    user_data = {
        "id": str(user.id),
        "login": user.login,
        "profil_id": str(user.profil_id) if user.profil_id else None,
        "stations_user": user.stations_user if user.stations_user else []
    }

    return {
        "success": True,
        "data": {
            "token": user_auth_result["access_token"],
            "user": user_data
        }
    }


@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        db_user = create_user(
            db,
            login=user.login,
            password=user.password,
            nom=user.nom,
            email=user.email,
            telephone=user.telephone,
            profil_id=user.profil_id,
            compagnie_id=user.compagnie_id,
            type_utilisateur=user.type_utilisateur
        )
        
        return {
            "success": True,
            "data": User(
                id=str(db_user.id),
                login=db_user.login,
                nom=db_user.nom,
                email=db_user.email,
                telephone=db_user.telephone,
                profil_id=str(db_user.profil_id) if db_user.profil_id else None,
                compagnie_id=str(db_user.compagnie_id) if db_user.compagnie_id else None,
                type_utilisateur=db_user.type_utilisateur,
                statut=db_user.statut,
                last_login=db_user.last_login.isoformat() if db_user.last_login else None,
                created_at=db_user.created_at.isoformat(),
                updated_at=db_user.updated_at.isoformat() if db_user.updated_at else None
            )
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user details by ID
    """
    # Check if current user has permission to view user details
    # This would typically require 'users.view' permission
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "data": User(
            id=str(user.id),
            login=user.login,
            nom=user.nom,
            email=user.email,
            telephone=user.telephone,
            profil_id=str(user.profil_id) if user.profil_id else None,
            compagnie_id=str(user.compagnie_id) if user.compagnie_id else None,
            type_utilisateur=user.type_utilisateur,
            statut=user.statut,
            last_login=user.last_login.isoformat() if user.last_login else None,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
    }


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_info(
    user_id: str,
    user_update: UserUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user information
    """
    # Check if current user has permission to update user details
    # This would typically require 'users.edit' permission
    
    updated_user = update_user(db, user_id, **user_update.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "data": User(
            id=str(updated_user.id),
            login=updated_user.login,
            nom=updated_user.nom,
            email=updated_user.email,
            telephone=updated_user.telephone,
            profil_id=str(updated_user.profil_id) if updated_user.profil_id else None,
            compagnie_id=str(updated_user.compagnie_id) if updated_user.compagnie_id else None,
            type_utilisateur=updated_user.type_utilisateur,
            statut=updated_user.statut,
            last_login=updated_user.last_login.isoformat() if updated_user.last_login else None,
            created_at=updated_user.created_at.isoformat(),
            updated_at=updated_user.updated_at.isoformat() if updated_user.updated_at else None
        )
    }


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user_endpoint(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logically delete a user (set status to 'Supprime')
    """
    # Check if current user has permission to delete users
    # This would typically require 'users.delete' permission
    
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "Utilisateur supprimé avec succès"
    }


@router.put("/users/{user_id}/activate", response_model=MessageResponse)
async def activate_user_endpoint(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activate a user
    """
    success = activate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "Utilisateur activé avec succès"
    }


@router.put("/users/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user_endpoint(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user
    """
    success = deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "Utilisateur désactivé avec succès"
    }


@router.post("/refresh-token", response_model=dict)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh an access token
    """
    # In a real implementation, you would validate the refresh token
    # For now, we'll just create a new access token
    
    # Extract user info from the refresh token
    payload = verify_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new access token
    new_token = create_refresh_token(db, user_id, endpoint_type=payload.get("type_endpoint", "utilisateur"))
    
    return {
        "success": True,
        "data": {
            "token": new_token,
            "refresh_token": token_data.refresh_token
        }
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout the current user
    """
    # In a real implementation, you would invalidate the token
    # For now, we just return success
    
    # This would typically involve adding the token to a blacklist
    success = logout_user(db, "")  # Token would be passed here in a real implementation
    
    return {
        "success": True,
        "message": "Déconnexion réussie"
    }


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout all sessions for the current user
    """
    # This would invalidate all tokens for the user
    sessions_count = logout_all_user_sessions(db, str(current_user.id))
    
    return {
        "success": True,
        "message": f"Toutes les sessions ({sessions_count}) ont été terminées"
    }


@router.get("/profile", response_model=dict)
async def get_user_profile(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile and permissions
    """
    profil = get_user_profil(db, str(current_user.id))
    permissions = get_permissions_for_user(db, str(current_user.id))
    
    profil_data = None
    if profil:
        profil_data = {
            "id": str(profil.id),
            "code": profil.code,
            "libelle": profil.libelle
        }
    
    permissions_data = [
        {
            "id": str(perm.id),
            "libelle": perm.libelle
        }
        for perm in permissions
    ]
    
    return {
        "success": True,
        "data": {
            "user": {
                "id": str(current_user.id),
                "login": current_user.login,
                "nom": current_user.nom,
                "email": current_user.email,
                "profil": profil_data,
                "permissions": permissions_data
            }
        }
    }