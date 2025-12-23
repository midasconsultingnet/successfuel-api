from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database.db_config import get_db
from ..auth.auth_handler import get_current_user_security
from ..services.tiers.tiers_solde_service import (
    calculer_solde_fournisseur,
    obtenir_solde_fournisseur,
    calculer_solde_achat
)
from .schemas import SoldeTiersResponse

router = APIRouter()

@router.get("/fournisseurs/{fournisseur_id}/solde", response_model=SoldeTiersResponse)
async def obtenir_solde_fournisseur(
    fournisseur_id: UUID,
    current_user = Depends(get_current_user_security),
    db: Session = Depends(get_db)
):
    """
    Récupérer le solde actuel d'un fournisseur.
    """
    # Vérifier que l'utilisateur a les droits d'accès
    # (ajouter les vérifications RBAC appropriées selon votre système)
    
    solde = obtenir_solde_fournisseur(db, fournisseur_id, current_user.station_id)
    
    if not solde:
        raise HTTPException(status_code=404, detail="Solde du fournisseur non trouvé")
    
    return solde


@router.get("/achats-carburant/{achat_id}/solde")
async def obtenir_solde_achat(
    achat_id: UUID,
    current_user = Depends(get_current_user_security),
    db: Session = Depends(get_db)
):
    """
    Récupérer le solde restant d'un achat spécifique.
    """
    # Vérifier que l'utilisateur a les droits d'accès
    # (ajouter les vérifications RBAC appropriées selon votre système)
    
    try:
        solde_restant = calculer_solde_achat(db, achat_id)
        return {
            "achat_id": achat_id,
            "solde_restant": solde_restant
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/fournisseurs/soldes")
async def obtenir_soldes_fournisseurs(
    current_user = Depends(get_current_user_security),
    db: Session = Depends(get_db)
):
    """
    Récupérer les soldes de tous les fournisseurs.
    """
    # TODO: Implémenter cette fonction pour renvoyer une liste de soldes
    # Pour l'instant, on renvoie une liste vide
    # Cette fonction devra être implémentée selon vos besoins spécifiques
    pass