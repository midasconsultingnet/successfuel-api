from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import date

from database.database import get_db
from models.comptabilite import (
    EcritureComptable, LigneEcriture, PlanComptable, Journal,
    SoldeCompte, BilanInitial, BilanInitialLigne
)
from schemas.comptabilite import (
    EcritureComptableCreate
)
from utils.access_control import require_permission, check_user_permission, create_permission_dependency
from models.structures import Utilisateur

router = APIRouter(tags=["Validation Comptable"])

@router.post("/verifier-ecriture-equilibree/")
async def verifier_ecriture_equilibree(
    ecriture_data: EcritureComptableCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("valider_ecritures_comptables"))
):
    """
    Vérifier si une écriture comptable est équilibrée avant de la valider
    """
    # Vérifier la permission
    if not check_user_permission(current_user, "valider_ecritures_comptables", ecriture_data.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    total_debit = sum(ligne.montant_debit for ligne in ecriture_data.lignes)
    total_credit = sum(ligne.montant_credit for ligne in ecriture_data.lignes)
    
    est_equilibree = abs(total_debit - total_credit) < 0.01  # Tolérance pour les arrondis
    
    return {
        "est_equilibree": est_equilibree,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "difference": abs(total_debit - total_credit)
    }

@router.post("/verifier-bilan-equilibre/")
async def verifier_bilan_equilibre(
    bilan_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("valider_bilan_initial"))
):
    """
    Vérifier si un bilan initial est équilibré (actif = passif + capitaux propres)
    """
    bilan = db.query(BilanInitial).filter(
        BilanInitial.id == bilan_id,
        BilanInitial.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not bilan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bilan initial non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(current_user, "valider_bilan_initial", bilan.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    total_actifs = db.query(func.sum(BilanInitialLigne.montant_initial)).filter(
        BilanInitialLigne.bilan_initial_id == bilan.id,
        BilanInitialLigne.poste_bilan == 'actif'
    ).scalar() or 0
    
    total_passif_capitaux = db.query(func.sum(BilanInitialLigne.montant_initial)).filter(
        BilanInitialLigne.bilan_initial_id == bilan.id,
        BilanInitialLigne.poste_bilan.in_(['passif', 'capitaux_propres'])
    ).scalar() or 0
    
    est_equilibre = abs(total_actifs - total_passif_capitaux) < 0.01  # Tolérance pour les arrondis
    
    return {
        "est_equilibre": est_equilibre,
        "total_actifs": total_actifs,
        "total_passif_plus_capitaux": total_passif_capitaux,
        "difference": abs(total_actifs - total_passif_capitaux)
    }