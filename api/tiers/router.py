from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from ..auth.auth_handler import get_current_user
from ..models import User
from .schemas import TiersResponse
from ..models.tiers import Tiers
from ..models.compagnie import Station

security = HTTPBearer()


# Dépendance pour obtenir l'utilisateur courant
async def get_current_active_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, token.credentials)
    return current_user

router = APIRouter(tags=["tiers"])


@router.get("/stations/{station_id}/clients", response_model=List[TiersResponse])
async def get_clients_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[TiersResponse]:
    """
    Récupérer tous les clients associés à une station spécifique
    """
    # Vérifier que la station appartient à la compagnie de l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer les clients associés à cette station
    clients = db.query(Tiers).filter(
        Tiers.type == "client",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.station_ids.op('?')(str(station_id))  # Vérifie si station_id est dans station_ids
    ).all()

    return clients


@router.get("/stations/{station_id}/fournisseurs", response_model=List[TiersResponse])
async def get_fournisseurs_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[TiersResponse]:
    """
    Récupérer tous les fournisseurs associés à une station spécifique
    """
    # Vérifier que la station appartient à la compagnie de l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer les fournisseurs associés à cette station
    fournisseurs = db.query(Tiers).filter(
        Tiers.type == "fournisseur",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.station_ids.op('?')(str(station_id))  # Vérifie si station_id est dans station_ids
    ).all()

    return fournisseurs


@router.get("/stations/{station_id}/employes", response_model=List[TiersResponse])
async def get_employes_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[TiersResponse]:
    """
    Récupérer tous les employés associés à une station spécifique
    """
    # Vérifier que la station appartient à la compagnie de l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer les employés associés à cette station
    employes = db.query(Tiers).filter(
        Tiers.type == "employe",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.station_ids.op('?')(str(station_id))  # Vérifie si station_id est dans station_ids
    ).all()

    return employes