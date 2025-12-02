from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database.database import get_db
from models.comptabilite import PlanComptable, Journal
from schemas.comptabilite import (
    PlanComptableCreate, PlanComptableUpdate, PlanComptableResponse,
    JournalCreate, JournalResponse, PlanComptableCreateRequest, JournalCreateRequest
)
from utils.access_control import require_permission, check_user_permission, create_permission_dependency
from models.structures import Utilisateur

router = APIRouter(tags=["Plan Comptable"])

@router.post("/", response_model=PlanComptableResponse, status_code=status.HTTP_201_CREATED)
async def create_plan_comptable(
    plan_data: PlanComptableCreateRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_plan_comptable"))
):
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "gerer_plan_comptable"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )

    # Vérifier si le numéro de compte existe déjà dans la compagnie de l'utilisateur
    existing_compte = db.query(PlanComptable).filter(
        PlanComptable.numero == plan_data.numero,
        PlanComptable.compagnie_id == current_user.compagnie_id
    ).first()

    if existing_compte:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le compte numéro {plan_data.numero} existe déjà pour cette compagnie"
        )

    # Créer le plan comptable en attribuant la compagnie de l'utilisateur connecté
    plan_comptable_data = plan_data.dict()
    plan_comptable_data['compagnie_id'] = current_user.compagnie_id
    plan_comptable = PlanComptable(**plan_comptable_data)

    db.add(plan_comptable)
    db.commit()
    db.refresh(plan_comptable)

    return plan_comptable

@router.get("/{plan_id}", response_model=PlanComptableResponse)
async def get_plan_comptable(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_plan_comptable"))
):
    plan_comptable = db.query(PlanComptable).filter(
        PlanComptable.id == plan_id,
        PlanComptable.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not plan_comptable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan comptable non trouvé"
        )
    
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "consulter_plan_comptable"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    return plan_comptable

@router.put("/{plan_id}", response_model=PlanComptableResponse)
async def update_plan_comptable(
    plan_id: str,
    plan_data: PlanComptableUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_plan_comptable"))
):
    plan_comptable = db.query(PlanComptable).filter(
        PlanComptable.id == plan_id,
        PlanComptable.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not plan_comptable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan comptable non trouvé"
        )
    
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "gerer_plan_comptable"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Mettre à jour les champs
    for field, value in plan_data.dict(exclude_unset=True).items():
        setattr(plan_comptable, field, value)
    
    db.commit()
    db.refresh(plan_comptable)
    
    return plan_comptable

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan_comptable(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_plan_comptable"))
):
    plan_comptable = db.query(PlanComptable).filter(
        PlanComptable.id == plan_id,
        PlanComptable.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not plan_comptable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan comptable non trouvé"
        )
    
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "gerer_plan_comptable"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    db.delete(plan_comptable)
    db.commit()
    
    return

@router.get("/", response_model=List[PlanComptableResponse])
async def list_plan_comptable(
    statut: Optional[str] = Query(None, description="Filtrer par statut (Actif, Inactif, Supprime)"),
    classe: Optional[str] = Query(None, description="Filtrer par classe comptable"),
    type_compte: Optional[str] = Query(None, description="Filtrer par type de compte"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_plan_comptable"))
):
    # Filtrer toujours par la compagnie de l'utilisateur connecté pour des raisons de sécurité
    query = db.query(PlanComptable).filter(PlanComptable.compagnie_id == current_user.compagnie_id)

    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "consulter_plan_comptable"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )

    if statut:
        query = query.filter(PlanComptable.statut == statut)

    if classe:
        query = query.filter(PlanComptable.classe == classe)

    if type_compte:
        query = query.filter(PlanComptable.type_compte == type_compte)

    plans = query.all()
    return plans

# Endpoints pour la gestion des journaux
@router.post("/journaux/", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
async def create_journal(
    journal_data: JournalCreateRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_journaux"))
):
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "gerer_journaux"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )

    # Vérifier si le code du journal existe déjà dans la compagnie de l'utilisateur
    existing_journal = db.query(Journal).filter(
        Journal.code == journal_data.code,
        Journal.compagnie_id == current_user.compagnie_id
    ).first()

    if existing_journal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le journal avec le code {journal_data.code} existe déjà pour cette compagnie"
        )

    # Créer le journal en attribuant la compagnie de l'utilisateur connecté
    journal_data_dict = journal_data.dict()
    journal_data_dict['compagnie_id'] = current_user.compagnie_id
    journal = Journal(**journal_data_dict)

    db.add(journal)
    db.commit()
    db.refresh(journal)

    return journal

@router.get("/journaux/", response_model=List[JournalResponse])
async def list_journaux(
    type_journal: Optional[str] = Query(None, description="Filtrer par type de journal"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_journaux"))
):
    query = db.query(Journal).filter(Journal.compagnie_id == current_user.compagnie_id)

    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "consulter_journaux"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )

    if type_journal:
        query = query.filter(Journal.type_journal == type_journal)

    if statut:
        query = query.filter(Journal.statut == statut)

    journaux = query.all()
    return journaux

@router.get("/journaux/{journal_id}", response_model=JournalResponse)
async def get_journal(
    journal_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_journaux"))
):
    journal = db.query(Journal).filter(
        Journal.id == journal_id,
        Journal.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(db, current_user.id, "consulter_journaux"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    return journal