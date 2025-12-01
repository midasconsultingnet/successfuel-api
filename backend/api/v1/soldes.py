from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import date

from database.database import get_db
from models.comptabilite import (
    EcritureComptable, LigneEcriture, PlanComptable,
    SoldeCompte, Journal
)
from schemas.comptabilite import SoldeCompteResponse
from utils.access_control import require_permission, check_user_permission, create_permission_dependency
from models.structures import Utilisateur

router = APIRouter(tags=["Soldes Comptables"])

@router.get("/compte/{compte_id}", response_model=SoldeCompteResponse)
async def get_solde_compte(
    compte_id: str,
    date_solde: date = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_soldes"))
):
    """
    Calculer le solde d'un compte à une date donnée
    """
    # Récupérer le compte pour vérifier l'appartenance à la compagnie
    compte = db.query(PlanComptable).filter(
        PlanComptable.id == compte_id
    ).first()
    
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(current_user, "consulter_soldes", compte.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Si aucune date n'est spécifiée, utiliser la date d'aujourd'hui
    if date_solde is None:
        date_solde = date.today()
    
    # Calculer le solde en additionnant les écritures de débit et crédit jusqu'à la date spécifiée
    result = db.query(
        func.sum(LigneEcriture.montant_debit).label('total_debit'),
        func.sum(LigneEcriture.montant_credit).label('total_credit')
    ).join(EcritureComptable).filter(
        LigneEcriture.compte_id == compte_id,
        EcritureComptable.date_ecriture <= date_solde,
        EcritureComptable.compagnie_id == compte.compagnie_id,
        EcritureComptable.est_validee == True  # Seulement les écritures validées
    ).first()
    
    # Créer un objet SoldeCompte à partir des résultats
    solde = SoldeCompte(
        compte_id=compte_id,
        date_solde=date_solde,
        solde_debit=result.total_debit or 0,
        solde_credit=result.total_credit or 0,
        type_solde='intermediaire',
        compagnie_id=compte.compagnie_id
    )
    
    return solde

@router.get("/compte/{compte_id}/historique")
async def get_historique_solde_compte(
    compte_id: str,
    date_debut: date = None,
    date_fin: date = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_soldes"))
):
    """
    Obtenir l'historique des soldes d'un compte sur une période
    """
    # Récupérer le compte pour vérifier l'appartenance à la compagnie
    compte = db.query(PlanComptable).filter(
        PlanComptable.id == compte_id
    ).first()
    
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(current_user, "consulter_soldes", compte.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Si aucune date de début n'est spécifiée, utiliser 30 jours avant aujourd'hui
    if date_debut is None:
        date_debut = date.today().replace(day=1)  # Premier jour du mois
    
    # Si aucune date de fin n'est spécifiée, utiliser aujourd'hui
    if date_fin is None:
        date_fin = date.today()
    
    # Récupérer les soldes existants dans la période
    soldes = db.query(SoldeCompte).filter(
        SoldeCompte.compte_id == compte_id,
        SoldeCompte.date_solde >= date_debut,
        SoldeCompte.date_solde <= date_fin,
        SoldeCompte.compagnie_id == compte.compagnie_id
    ).order_by(SoldeCompte.date_solde).all()
    
    return soldes

@router.get("/journal/{journal_id}")
async def get_soldes_journal(
    journal_id: str,
    date_debut: date = None,
    date_fin: date = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_soldes"))
):
    """
    Calculer les soldes des comptes pour un journal spécifique sur une période
    """
    # Vérifier l'existence du journal
    journal = db.query(Journal).filter(
        Journal.id == journal_id
    ).first()
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(current_user, "consulter_soldes", journal.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Si aucune date de début n'est spécifiée, utiliser 30 jours avant aujourd'hui
    if date_debut is None:
        date_debut = date.today().replace(day=1)  # Premier jour du mois
    
    # Si aucune date de fin n'est spécifiée, utiliser aujourd'hui
    if date_fin is None:
        date_fin = date.today()
    
    # Calculer le solde de chaque compte affecté par ce journal
    soldes = db.query(
        PlanComptable.id.label('compte_id'),
        PlanComptable.numero.label('compte_numero'),
        PlanComptable.intitule.label('compte_intitule'),
        func.sum(LigneEcriture.montant_debit).label('total_debit'),
        func.sum(LigneEcriture.montant_credit).label('total_credit')
    ).join(LigneEcriture, PlanComptable.id == LigneEcriture.compte_id)\
     .join(EcritureComptable, LigneEcriture.ecriture_id == EcritureComptable.id)\
     .filter(
         EcritureComptable.journal_id == journal_id,
         EcritureComptable.date_ecriture >= date_debut,
         EcritureComptable.date_ecriture <= date_fin,
         EcritureComptable.compagnie_id == journal.compagnie_id,
         EcritureComptable.est_validee == True  # Seulement les écritures validées
     ).group_by(PlanComptable.id, PlanComptable.numero, PlanComptable.intitule).all()
    
    # Formater les résultats
    result = []
    for solde in soldes:
        result.append({
            "compte_id": solde.compte_id,
            "compte_numero": solde.compte_numero,
            "compte_intitule": solde.compte_intitule,
            "total_debit": float(solde.total_debit or 0),
            "total_credit": float(solde.total_credit or 0),
            "solde_net": float((solde.total_debit or 0) - (solde.total_credit or 0))
        })
    
    return result