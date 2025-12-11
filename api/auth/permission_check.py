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


def check_resource_access(db: Session, user: User, resource_id: str, resource_type: str):
    """
    Vérifie si l'utilisateur a accès à une ressource spécifique.
    resource_type peut être 'station', 'cuve', 'pistolet', 'produit', 'stock'
    """
    # Vérifier selon le type de ressource
    if resource_type == 'station':
        from ..models import Station as StationModel, Compagnie as CompagnieModel
        resource = db.query(StationModel).join(CompagnieModel).filter(
            StationModel.id == resource_id,
            CompagnieModel.id == user.compagnie_id
        ).first()
    elif resource_type == 'cuve':
        from ..models import Cuve as CuveModel, Station as StationModel
        from ..models.compagnie import Compagnie
        resource = db.query(CuveModel).join(StationModel).join(Compagnie).filter(
            CuveModel.id == resource_id,
            Compagnie.id == user.compagnie_id
        ).first()
    elif resource_type == 'pistolet':
        from ..models import Pistolet as PistoletModel, Cuve as CuveModel, Station as StationModel
        from ..models.compagnie import Compagnie
        resource = db.query(PistoletModel).join(CuveModel).join(StationModel).join(Compagnie).filter(
            PistoletModel.id == resource_id,
            Compagnie.id == user.compagnie_id
        ).first()
    elif resource_type == 'produit':
        from ..models import Produit as ProduitModel, Station as StationModel
        from ..models.compagnie import Compagnie
        resource = db.query(ProduitModel).join(StationModel).join(Compagnie).filter(
            ProduitModel.id == resource_id,
            Compagnie.id == user.compagnie_id
        ).first()
    elif resource_type == 'stock':
        from ..models import StockProduit as StockProduitModel, Produit as ProduitModel, Station as StationModel
        from ..models.compagnie import Compagnie
        resource = db.query(StockProduitModel).join(ProduitModel).join(StationModel).join(Compagnie).filter(
            StockProduitModel.id == resource_id,
            Compagnie.id == user.compagnie_id
        ).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource type {resource_type} not supported"
        )

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to this {resource_type}"
        )

    return resource