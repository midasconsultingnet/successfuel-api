from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.database import get_db
from models.securite import TentativeConnexion, EvenementSecurite, ModificationSensible, TentativeAccesNonAutorise
from services.auth_service import get_user_by_id
from utils.security import verify_token
from utils.dependencies import get_current_user


# Security logging and monitoring API
# Ce module gère la journalisation et la surveillance de sécurité
router = APIRouter(
    prefix="/security",
    tags=["security_logs"],
    responses={404: {"description": "Endpoint non trouvé"}}
)


# Request/response models
from pydantic import BaseModel


class PaginationResponse(BaseModel):
    total: int
    limit: int
    offset: int


class LoginAttempt(BaseModel):
    id: str
    login: str
    ip_connexion: Optional[str] = None
    resultat_connexion: str
    utilisateur_id: Optional[str] = None
    created_at: str


class LoginAttemptsResponse(BaseModel):
    success: bool
    pagination: PaginationResponse
    data: List[LoginAttempt]


class SecurityEvent(BaseModel):
    id: str
    type_evenement: str
    description: Optional[str] = None
    utilisateur_id: Optional[str] = None
    ip_utilisateur: Optional[str] = None
    poste_utilisateur: Optional[str] = None
    donnees_supplementaires: Optional[dict] = None
    statut: str
    created_at: str


class SecurityEventsResponse(BaseModel):
    success: bool
    pagination: PaginationResponse
    data: List[SecurityEvent]


class SensitiveModification(BaseModel):
    id: str
    type_operation: str
    objet_modifie: str
    objet_id: Optional[str] = None
    ancienne_valeur: Optional[dict] = None
    nouvelle_valeur: Optional[dict] = None
    seuil_alerte: bool
    commentaire: Optional[str] = None
    ip_utilisateur: Optional[str] = None
    poste_utilisateur: Optional[str] = None
    statut: str
    created_at: str


class SensitiveModificationsResponse(BaseModel):
    success: bool
    pagination: PaginationResponse
    data: List[SensitiveModification]


class UnauthorizedAccessAttempt(BaseModel):
    id: str
    utilisateur_id: Optional[str] = None
    endpoint_accesse: str
    endpoint_autorise: Optional[str] = None
    ip_connexion: Optional[str] = None
    statut: str
    created_at: str


class UnauthorizedAccessResponse(BaseModel):
    success: bool
    pagination: PaginationResponse
    data: List[UnauthorizedAccessAttempt]




@router.get("/login-attempts", response_model=LoginAttemptsResponse)
async def get_login_attempts(
    date_debut: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    resultat: Optional[str] = Query(None, description="Result: REUSSIE or ECHEC"),
    utilisateur_id: Optional[str] = Query(None, description="User ID"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get login attempts with optional filters
    """
    query = db.query(TentativeConnexion)
    
    # Apply filters
    if date_debut:
        try:
            start_date = datetime.strptime(date_debut, "%Y-%m-%d")
            query = query.filter(TentativeConnexion.created_at >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_debut")
    
    if date_fin:
        try:
            end_date = datetime.strptime(date_fin, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(TentativeConnexion.created_at < end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_fin")
    
    if resultat:
        result_filter = resultat.upper()
        if result_filter not in ["REUSSIE", "ECHEC"]:
            raise HTTPException(status_code=400, detail="Invalid result value. Use REUSSIE or ECHEC")
        result_db = "Reussie" if result_filter == "REUSSIE" else "Echouee"
        query = query.filter(TentativeConnexion.resultat_connexion == result_db)
    
    if utilisateur_id:
        query = query.filter(TentativeConnexion.utilisateur_id == utilisateur_id)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    login_attempts = query.offset(offset).limit(limit).all()
    
    return LoginAttemptsResponse(
        success=True,
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        ),
        data=[
            LoginAttempt(
                id=str(attempt.id),
                login=attempt.login,
                ip_connexion=attempt.ip_connexion,
                resultat_connexion=attempt.resultat_connexion,
                utilisateur_id=str(attempt.utilisateur_id) if attempt.utilisateur_id else None,
                created_at=attempt.created_at.isoformat()
            )
            for attempt in login_attempts
        ]
    )


@router.get("/security-events", response_model=SecurityEventsResponse)
async def get_security_events(
    date_debut: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    type_evenement: Optional[str] = Query(None, description="Event type"),
    utilisateur_id: Optional[str] = Query(None, description="User ID"),
    statut: Optional[str] = Query(None, description="Status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get security events with optional filters
    """
    query = db.query(EvenementSecurite)
    
    # Apply filters
    if date_debut:
        try:
            start_date = datetime.strptime(date_debut, "%Y-%m-%d")
            query = query.filter(EvenementSecurite.created_at >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_debut")
    
    if date_fin:
        try:
            end_date = datetime.strptime(date_fin, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(EvenementSecurite.created_at < end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_fin")
    
    if type_evenement:
        query = query.filter(EvenementSecurite.type_evenement == type_evenement)
    
    if utilisateur_id:
        query = query.filter(EvenementSecurite.utilisateur_id == utilisateur_id)
    
    if statut:
        query = query.filter(EvenementSecurite.statut == statut)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    events = query.offset(offset).limit(limit).all()
    
    return SecurityEventsResponse(
        success=True,
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        ),
        data=[
            SecurityEvent(
                id=str(event.id),
                type_evenement=event.type_evenement,
                description=event.description,
                utilisateur_id=str(event.utilisateur_id) if event.utilisateur_id else None,
                ip_utilisateur=event.ip_utilisateur,
                poste_utilisateur=event.poste_utilisateur,
                donnees_supplementaires=event.donnees_supplementaires,
                statut=event.statut,
                created_at=event.created_at.isoformat()
            )
            for event in events
        ]
    )


@router.get("/sensitive-modifications", response_model=SensitiveModificationsResponse)
async def get_sensitive_modifications(
    date_debut: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    objet_modifie: Optional[str] = Query(None, description="Object modified"),
    utilisateur_id: Optional[str] = Query(None, description="User ID"),
    seuil_alerte: Optional[bool] = Query(None, description="Threshold alert"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get sensitive modifications with optional filters
    """
    query = db.query(ModificationSensible)
    
    # Apply filters
    if date_debut:
        try:
            start_date = datetime.strptime(date_debut, "%Y-%m-%d")
            query = query.filter(ModificationSensible.created_at >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_debut")
    
    if date_fin:
        try:
            end_date = datetime.strptime(date_fin, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(ModificationSensible.created_at < end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_fin")
    
    if objet_modifie:
        query = query.filter(ModificationSensible.objet_modifie == objet_modifie)
    
    if utilisateur_id:
        query = query.filter(ModificationSensible.utilisateur_id == utilisateur_id)
    
    if seuil_alerte is not None:
        query = query.filter(ModificationSensible.seuil_alerte == seuil_alerte)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    modifications = query.offset(offset).limit(limit).all()
    
    return SensitiveModificationsResponse(
        success=True,
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        ),
        data=[
            SensitiveModification(
                id=str(mod.id),
                type_operation=mod.type_operation,
                objet_modifie=mod.objet_modifie,
                objet_id=str(mod.objet_id) if mod.objet_id else None,
                ancienne_valeur=mod.ancienne_valeur,
                nouvelle_valeur=mod.nouvelle_valeur,
                seuil_alerte=mod.seuil_alerte,
                commentaire=mod.commentaire,
                ip_utilisateur=mod.ip_utilisateur,
                poste_utilisateur=mod.poste_utilisateur,
                statut=mod.statut,
                created_at=mod.created_at.isoformat()
            )
            for mod in modifications
        ]
    )


@router.get("/unauthorized-access", response_model=UnauthorizedAccessResponse)
async def get_unauthorized_access_attempts(
    date_debut: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    utilisateur_id: Optional[str] = Query(None, description="User ID"),
    endpoint_accesse: Optional[str] = Query(None, description="Accessed endpoint"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unauthorized access attempts with optional filters
    """
    query = db.query(TentativeAccesNonAutorise)
    
    # Apply filters
    if date_debut:
        try:
            start_date = datetime.strptime(date_debut, "%Y-%m-%d")
            query = query.filter(TentativeAccesNonAutorise.created_at >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_debut")
    
    if date_fin:
        try:
            end_date = datetime.strptime(date_fin, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(TentativeAccesNonAutorise.created_at < end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for date_fin")
    
    if utilisateur_id:
        query = query.filter(TentativeAccesNonAutorise.utilisateur_id == utilisateur_id)
    
    if endpoint_accesse:
        query = query.filter(TentativeAccesNonAutorise.endpoint_accesse == endpoint_accesse)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    attempts = query.offset(offset).limit(limit).all()
    
    return UnauthorizedAccessResponse(
        success=True,
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        ),
        data=[
            UnauthorizedAccessAttempt(
                id=str(attempt.id),
                utilisateur_id=str(attempt.utilisateur_id) if attempt.utilisateur_id else None,
                endpoint_accesse=attempt.endpoint_accesse,
                endpoint_autorise=attempt.endpoint_autorise,
                ip_connexion=attempt.ip_connexion,
                statut=attempt.statut,
                created_at=attempt.created_at.isoformat()
            )
            for attempt in attempts
        ]
    )