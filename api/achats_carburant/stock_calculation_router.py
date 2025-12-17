from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..services.achats_carburant.stock_calculation_service import StockCalculationService
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..rbac_decorators import require_permission

router = APIRouter()
security = HTTPBearer()

@router.get("/cuves/{cuve_id}/stock_theorique/{date_livraison}", 
            response_model=dict, 
            dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def get_stock_theorique_cuve(
    cuve_id: str,  # UUID as string
    date_livraison: str,  # Date as string in YYYY-MM-DD format
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Calcule le stock théorique d'une cuve à une date donnée en se basant 
    sur l'état initial et toutes les livraisons effectuées jusqu'à cette date.
    """
    try:
        # Convert date string to datetime
        date_livraison_obj = datetime.fromisoformat(date_livraison.replace("Z", "+00:00"))
        
        # Calculate theoretical stock
        result = StockCalculationService.calculer_stock_theorique_apres_livraison(
            db, UUID(cuve_id), date_livraison_obj
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du stock théorique: {str(e)}")


@router.post("/livraisons/{livraison_id}/verifier_compensations", 
             response_model=dict, 
             dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def verifier_et_creer_compensations_auto(
    livraison_id: str,  # UUID as string
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Vérifie s'il y a des écarts entre les quantités commandées et livrées
    et crée automatiquement des compensations si nécessaires.
    """
    try:
        # Vérifier et créer les compensations automatiques
        compensation = StockCalculationService.verifier_et_creer_compensations_automatiques(
            db, UUID(livraison_id)
        )
        
        if compensation:
            return {
                "message": "Compensation automatique créée avec succès",
                "compensation_id": str(compensation.id)
            }
        else:
            return {
                "message": "Aucune compensation nécessaire",
                "compensation_id": None
            }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification des compensations: {str(e)}")


@router.get("/livraisons/{livraison_id}/verification_ecarts", 
            response_model=dict, 
            dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def get_verification_ecarts_livraison_achat(
    livraison_id: str,  # UUID as string
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Vérifie les écarts entre les quantités prévues dans les commandes et les quantités réellement livrées.
    """
    try:
        result = StockCalculationService.verifier_ecarts_livraison_achat(
            db, UUID(livraison_id)
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification des écarts: {str(e)}")