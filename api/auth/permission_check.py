from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from ..models import User, AffectationUtilisateurStation
from .auth_handler import get_current_user
from sqlalchemy import and_
import uuid


def check_station_access(db: Session, user: User, station_id: str, required_role: str = None):
    """
    Vérifie si l'utilisateur a accès à la station spécifiée
    """
    # Si un rôle spécifique est requis, vérifiez-le
    if required_role and user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {required_role}"
        )
    
    # Vérifiez si l'utilisateur est affecté à cette station
    affectation = db.query(AffectationUtilisateurStation).filter(
        and_(
            AffectationUtilisateurStation.utilisateur_id == user.id,
            AffectationUtilisateurStation.station_id == station_id
        )
    ).first()
    
    if not affectation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this station"
        )
    
    # Vérifiez également que l'utilisateur et la station appartiennent à la même compagnie
    # (cette vérification dépend de la structure exacte des données)


def check_company_access(db: Session, user: User, compagnie_id: str):
    """
    Vérifie si l'utilisateur appartient à la compagnie spécifiée
    """
    if str(user.compagnie_id) != compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this company"
        )