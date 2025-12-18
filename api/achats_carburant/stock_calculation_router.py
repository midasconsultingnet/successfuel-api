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

router = APIRouter(
    prefix="/stock-calculation",
    tags=["Achats carburant"]
)
security = HTTPBearer()

@router.get("/cuves/{cuve_id}/stock_theorique/{date_livraison}",
            response_model=dict,
            summary="Calculer le stock théorique d'une cuve",
            description="Calcule le stock théorique d'une cuve à une date donnée en se basant sur l'état initial et toutes les livraisons de carburant effectuées jusqu'à cette date. Nécessite la permission 'Module Achats Carburant'.")
async def get_stock_theorique_cuve(
    cuve_id: str,  # UUID as string
    date_livraison: str,  # Date as string in YYYY-MM-DD format
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Calcule le stock théorique d'une cuve à une date donnée en se basant
    sur l'état initial et toutes les livraisons de carburant effectuées jusqu'à cette date.
    Cette fonction utilise les données de livraison enregistrées dans le module Livraisons
    pour effectuer les calculs de stock théorique.

    Args:
        cuve_id (str): L'identifiant de la cuve
        date_livraison (str): La date de livraison au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        dict: Résultats du calcul du stock théorique

    Raises:
        HTTPException: Si la date de livraison est invalide ou si une erreur survient lors du calcul
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
             summary="Vérifier et créer des compensations automatiques",
             description="Vérifie s'il y a des écarts entre les quantités commandées et livrées et crée automatiquement des compensations si nécessaires. Nécessite la permission 'Module Achats Carburant'.")
async def verifier_et_creer_compensations_auto(
    livraison_id: str,  # UUID as string
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Vérifie s'il y a des écarts entre les quantités commandées dans les achats
    et les quantités réellement livrées (enregistrées dans le module Livraisons),
    et crée automatiquement des compensations si nécessaires.

    Args:
        livraison_id (str): L'identifiant de la livraison (provenant du module Livraisons)
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        dict: Résultats de la vérification et création de compensations

    Raises:
        HTTPException: Si la livraison n'est pas trouvée ou si une erreur survient
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
            summary="Vérifier les écarts de livraison",
            description="Vérifie les écarts entre les quantités prévues dans les commandes et les quantités réellement livrées. Nécessite la permission 'Module Achats Carburant'.")
async def get_verification_ecarts_livraison_achat(
    livraison_id: str,  # UUID as string
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Vérifie les écarts entre les quantités prévues dans les commandes d'achat
    et les quantités réellement livrées (enregistrées dans le module Livraisons).

    Args:
        livraison_id (str): L'identifiant de la livraison (provenant du module Livraisons)
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        dict: Résultats de la vérification des écarts

    Raises:
        HTTPException: Si la livraison n'est pas trouvée ou si une erreur survient
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