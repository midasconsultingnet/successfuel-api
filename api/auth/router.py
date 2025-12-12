from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_, func
from ..database import get_db
from ..models import User as UserModel, AffectationUtilisateurStation as AffectationModel, JournalActionUtilisateur as JournalModel
from . import schemas
from .auth_handler import authenticate_user, get_current_user, get_password_hash, create_tokens_for_user, get_user_from_refresh_token
from .journalisation import log_user_action
from .permission_check import check_company_access
from ..translations import get_translation

router = APIRouter()
security = HTTPBearer()

@router.post("/login")
async def login(user_credentials: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.login, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_translation("invalid_credentials", request.state.lang, "auth"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = create_tokens_for_user(db, user)

    # Définir le refresh_token dans un cookie HTTPONLY
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer"
    })
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Nécessite HTTPS
        samesite="lax",  # Protection CSRF
        max_age=7*24*60*60  # 7 jours en secondes
    )

    return response


@router.post("/refresh")
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    # Récupérer le refresh_token depuis le cookie
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": get_translation("invalid_refresh_token", request.state.lang, "auth")
            }
        )
        response.delete_cookie("refresh_token")
        return response

    try:
        user, token_entry = get_user_from_refresh_token(db, refresh_token)

        # Mark old token as inactive
        token_entry.actif = False
        db.commit()

        # Create new tokens
        new_access_token, new_refresh_token = create_tokens_for_user(db, user)

        # Set the new refresh token in the cookie
        response = JSONResponse(content={
            "access_token": new_access_token,
            "token_type": "bearer"
        })
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,  # Utilisation du nouveau token
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7*24*60*60  # 7 jours
        )

        return response
    except Exception:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": get_translation("invalid_refresh_token", request.state.lang, "auth")
            }
        )
        response.delete_cookie("refresh_token")
        return response


@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        # Récupérer l'utilisateur à partir du jeton d'accès
        from .auth_handler import get_current_user
        current_user = get_current_user(db, token)

        # Trouver et désactiver le token de rafraîchissement associé
        from ..models import TokenSession
        from datetime import datetime
        from sqlalchemy import and_

        # Récupérer le refresh_token depuis le cookie
        refresh_token = request.cookies.get("refresh_token")

        if refresh_token:
            # Trouver l'entrée dans la base de données
            token_entry = db.query(TokenSession).filter(
                and_(
                    TokenSession.utilisateur_id == current_user.id,
                    TokenSession.token_refresh == refresh_token,
                    TokenSession.actif == True
                )
            ).first()

            if token_entry:
                # Marquer comme inactif
                token_entry.actif = False
                db.commit()

    except Exception:
        # Si le token est invalide, on continue quand même
        pass

    # Supprimer le cookie de refresh_token et retourner la réponse
    from fastapi.responses import JSONResponse
    response = JSONResponse(content={"message": get_translation("logged_out_successfully", request.state.lang)})
    response.delete_cookie("refresh_token")
    return response


@router.get("/users", response_model=List[schemas.UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify the user is authenticated
    token = credentials.credentials
    current_user = get_current_user(db, token)

    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=schemas.UserResponse)
async def create_user(
    user: schemas.UserCreate,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Vérifier l'utilisateur connecté
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier les permissions (seuls les administrateurs peuvent créer des utilisateurs)
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_translation("insufficient_permissions", request.state.lang, "auth")
        )

    # Vérifier que l'utilisateur appartient à la même compagnie
    check_company_access(db, current_user, user.compagnie_id)

    # Check if user already exists
    db_user = db.query(UserModel).filter(UserModel.login == user.login).first()
    if db_user:
        raise HTTPException(status_code=400, detail=get_translation("login_already_registered", request.state.lang))

    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail=get_translation("email_already_registered", request.state.lang))

    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create the user
    db_user = UserModel(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        login=user.login,
        mot_de_passe_hash=hashed_password,
        role=user.role,
        compagnie_id=user.compagnie_id
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="user_management",
        donnees_apres=db_user.__dict__,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_user


@router.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    current_user = get_current_user(db, token)
    return current_user


@router.put("/users/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_update: schemas.UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    current_user = get_current_user(db, token)

    if user_update.nom is not None:
        current_user.nom = user_update.nom
    if user_update.prenom is not None:
        current_user.prenom = user_update.prenom
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(UserModel).filter(
            UserModel.email == user_update.email,
            UserModel.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail=get_translation("email_already_registered_by_another_user", request.state.lang))
        current_user.email = user_update.email
    if user_update.login is not None:
        # Check if login is already taken by another user
        existing_user = db.query(UserModel).filter(
            UserModel.login == user_update.login,
            UserModel.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail=get_translation("login_already_registered_by_another_user", request.state.lang))
        current_user.login = user_update.login
    if user_update.role is not None:
        current_user.role = user_update.role
    if user_update.actif is not None:
        current_user.actif = user_update.actif

    if user_update.password is not None:
        current_user.mot_de_passe_hash = get_password_hash(user_update.password)

    current_user.updated_at = func.now()
    db.commit()
    db.refresh(current_user)

    return current_user


# Endpoints pour gérer l'affectation utilisateur-station
@router.get("/users/{user_id}/stations", response_model=List[schemas.AffectationUtilisateurStationResponse])
async def get_user_stations(
    user_id: str,  # UUID as string
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify the user is authenticated
    token = credentials.credentials
    current_user = get_current_user(db, token)

    # In a real implementation, verify permissions to access this resource
    affectations = db.query(AffectationModel).filter(AffectationModel.utilisateur_id == user_id).all()
    return affectations


@router.post("/users/{user_id}/stations", response_model=schemas.AffectationUtilisateurStationResponse)
async def assign_user_to_station(
    user_id: str,  # UUID as string
    affectation: schemas.AffectationUtilisateurStationCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify the user is authenticated
    token = credentials.credentials
    current_user = get_current_user(db, token)

    # Verify the user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the assignment already exists
    existing_affectation = db.query(AffectationModel).filter(
        and_(
            AffectationModel.utilisateur_id == user_id,
            AffectationModel.station_id == affectation.station_id
        )
    ).first()

    if existing_affectation:
        raise HTTPException(status_code=400, detail="User is already assigned to this station")

    # Create the assignment
    db_affectation = AffectationModel(
        utilisateur_id=user_id,
        station_id=affectation.station_id
    )

    db.add(db_affectation)
    db.commit()
    db.refresh(db_affectation)

    return db_affectation


@router.delete("/users/{user_id}/stations/{station_id}")
async def remove_user_from_station(
    user_id: str,  # UUID as string
    station_id: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify the user is authenticated
    token = credentials.credentials
    current_user = get_current_user(db, token)

    # Delete the assignment
    affectation = db.query(AffectationModel).filter(
        and_(
            AffectationModel.utilisateur_id == user_id,
            AffectationModel.station_id == station_id
        )
    ).first()

    if not affectation:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(affectation)
    db.commit()

    return {"message": "User successfully removed from station"}
