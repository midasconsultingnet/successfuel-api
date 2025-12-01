from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import date, datetime

from database.database import get_db
from models.comptabilite import (
    EcritureComptable, LigneEcriture, PlanComptable, Journal, SoldeCompte
)
from schemas.comptabilite import (
    EcritureComptableCreate, EcritureComptableUpdate, EcritureComptableResponse
)
from utils.access_control import require_permission, check_user_permission, create_permission_dependency
from models.structures import Utilisateur

router = APIRouter(tags=["Écritures Comptables"])

@router.post("/", response_model=EcritureComptableResponse, status_code=status.HTTP_201_CREATED)
async def create_ecriture_comptable(
    ecriture_data: EcritureComptableCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_ecritures_comptables"))
):
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "gerer_ecritures_comptables"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Vérifier que l'utilisateur a accès au journal
    journal = db.query(Journal).filter(
        Journal.id == ecriture_data.journal_id,
        Journal.compagnie_id == ecriture_data.compagnie_id
    ).first()
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal non trouvé ou inaccessible"
        )
    
    # Vérifier que toutes les lignes utilisent des comptes valides
    compte_ids = [ligne.compte_id for ligne in ecriture_data.lignes]
    comptes = db.query(PlanComptable).filter(
        PlanComptable.id.in_(compte_ids),
        PlanComptable.compagnie_id == ecriture_data.compagnie_id
    ).all()
    
    if len(comptes) != len(compte_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un ou plusieurs comptes spécifiés n'existent pas ou sont inaccessibles"
        )
    
    # Vérifier que l'écriture est équilibrée (débit = crédit)
    total_debit = sum(ligne.montant_debit for ligne in ecriture_data.lignes)
    total_credit = sum(ligne.montant_credit for ligne in ecriture_data.lignes)
    
    if abs(total_debit - total_credit) > 0.01:  # Tolérance pour les arrondis
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"L'écriture n'est pas équilibrée: débit {total_debit} != crédit {total_credit}"
        )
    
    # Générer le numéro de pièce
    journal.derniere_piece += 1
    numero_piece = f"{journal.code}-{ecriture_data.date_ecriture.strftime('%Y%m')}-{journal.derniere_piece:03d}"
    
    # Créer l'écriture comptable
    ecriture = EcritureComptable(
        journal_id=ecriture_data.journal_id,
        numero_piece=numero_piece,
        date_ecriture=ecriture_data.date_ecriture,
        libelle=ecriture_data.libelle,
        tiers_id=ecriture_data.tiers_id,
        operation_id=ecriture_data.operation_id,
        operation_type=ecriture_data.operation_type,
        reference_externe=ecriture_data.reference_externe,
        compagnie_id=ecriture_data.compagnie_id,
        utilisateur_id=current_user.id,
        montant_debit=total_debit,
        montant_credit=total_credit
    )
    
    db.add(ecriture)
    db.flush()  # Pour obtenir l'ID de l'écriture avant de créer les lignes
    
    # Créer les lignes d'écriture
    for ligne_data in ecriture_data.lignes:
        ligne = LigneEcriture(
            ecriture_id=ecriture.id,
            compte_id=ligne_data.compte_id,
            montant_debit=ligne_data.montant_debit,
            montant_credit=ligne_data.montant_credit,
            libelle=ligne_data.libelle,
            tiers_id=ligne_data.tiers_id,
            projet_id=ligne_data.projet_id
        )
        db.add(ligne)
    
    # Mettre à jour les soldes des comptes concernés
    for ligne_data in ecriture_data.lignes:
        # Créer ou mettre à jour le solde du compte
        solde_existant = db.query(SoldeCompte).filter(
            SoldeCompte.compte_id == ligne_data.compte_id,
            SoldeCompte.date_solde == ecriture_data.date_ecriture,
            SoldeCompte.compagnie_id == ecriture_data.compagnie_id
        ).first()
        
        if solde_existant:
            # Mettre à jour le solde existant
            if ligne_data.montant_debit > 0:
                solde_existant.solde_debit += ligne_data.montant_debit
            if ligne_data.montant_credit > 0:
                solde_existant.solde_credit += ligne_data.montant_credit
        else:
            # Créer un nouveau solde
            solde = SoldeCompte(
                compte_id=ligne_data.compte_id,
                date_solde=ecriture_data.date_ecriture,
                solde_debit=ligne_data.montant_debit if ligne_data.montant_debit > 0 else 0,
                solde_credit=ligne_data.montant_credit if ligne_data.montant_credit > 0 else 0,
                type_solde='intermediaire',
                compagnie_id=ecriture_data.compagnie_id
            )
            db.add(solde)
    
    db.commit()
    db.refresh(ecriture)
    
    # Recharger l'écriture avec ses lignes
    ecriture = db.query(EcritureComptable).filter(EcritureComptable.id == ecriture.id).first()
    
    return ecriture

@router.get("/{ecriture_id}", response_model=EcritureComptableResponse)
async def get_ecriture_comptable(
    ecriture_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_ecritures_comptables"))
):
    ecriture = db.query(EcritureComptable).filter(
        EcritureComptable.id == ecriture_id,
        EcritureComptable.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not ecriture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Écriture comptable non trouvée"
        )
    
    # Vérifier la permission
    if not check_user_permission(db, current_user.id, "consulter_ecritures_comptables"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    return ecriture

@router.put("/{ecriture_id}", response_model=EcritureComptableResponse)
async def update_ecriture_comptable(
    ecriture_id: str,
    ecriture_data: EcritureComptableUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_ecritures_comptables"))
):
    ecriture = db.query(EcritureComptable).filter(
        EcritureComptable.id == ecriture_id,
        EcritureComptable.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not ecriture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Écriture comptable non trouvée"
        )
    
    # Vérifier la permission
    if not check_user_permission(db, current_user.id, "gerer_ecritures_comptables"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Ne permettre la modification que si l'écriture n'est pas validée
    if ecriture.est_validee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de modifier une écriture déjà validée"
        )
    
    # Mettre à jour les champs
    for field, value in ecriture_data.dict(exclude_unset=True).items():
        setattr(ecriture, field, value)
    
    if ecriture_data.est_validee:
        ecriture.date_validation = datetime.now()
        ecriture.utilisateur_validation_id = current_user.id
    
    db.commit()
    db.refresh(ecriture)
    
    return ecriture

@router.delete("/{ecriture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ecriture_comptable(
    ecriture_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_ecritures_comptables"))
):
    ecriture = db.query(EcritureComptable).filter(
        EcritureComptable.id == ecriture_id,
        EcritureComptable.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not ecriture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Écriture comptable non trouvée"
        )
    
    # Vérifier la permission
    if not check_user_permission(db, current_user.id, "gerer_ecritures_comptables"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Ne permettre la suppression que si l'écriture n'est pas validée
    if ecriture.est_validee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer une écriture déjà validée"
        )
    
    db.delete(ecriture)
    db.commit()
    
    return

@router.get("/", response_model=List[EcritureComptableResponse])
async def list_ecritures_comptables(
    compagnie_id: str = None,
    journal_id: str = None,
    date_debut: date = None,
    date_fin: date = None,
    est_validee: bool = None,
    tiers_id: str = None,
    operation_type: str = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_ecritures_comptables"))
):
    query = db.query(EcritureComptable).filter(
        EcritureComptable.compagnie_id == (compagnie_id or current_user.compagnie_id)
    )
    
    # Vérifier la permission
    user_compagnie_id = compagnie_id or current_user.compagnie_id
    if not check_user_permission(db, current_user.id, "consulter_ecritures_comptables"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    if journal_id:
        query = query.filter(EcritureComptable.journal_id == journal_id)
    
    if date_debut:
        query = query.filter(EcritureComptable.date_ecriture >= date_debut)
    
    if date_fin:
        query = query.filter(EcritureComptable.date_ecriture <= date_fin)
    
    if est_validee is not None:
        query = query.filter(EcritureComptable.est_validee == est_validee)
    
    if tiers_id:
        query = query.filter(EcritureComptable.tiers_id == tiers_id)
    
    if operation_type:
        query = query.filter(EcritureComptable.operation_type == operation_type)
    
    # Trier par date et numéro de pièce
    query = query.order_by(EcritureComptable.date_ecriture.desc(), EcritureComptable.numero_piece.desc())
    
    ecritures = query.all()
    return ecritures