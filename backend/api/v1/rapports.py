from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import date

from database.database import get_db
from models.comptabilite import RapportFinancier, HistoriqueRapport
from schemas.comptabilite import (
    RapportFinancierCreate, RapportFinancierUpdate, RapportFinancierResponse,
    HistoriqueRapportCreate, HistoriqueRapportResponse
)
from utils.access_control import require_permission, check_user_permission, create_permission_dependency
from models.structures import Utilisateur

router = APIRouter(tags=["Rapports"])

# Endpoints pour les rapports financiers
@router.post("/financiers/", response_model=RapportFinancierResponse, status_code=status.HTTP_201_CREATED)
async def create_rapport_financier(
    rapport_data: RapportFinancierCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("generer_rapports"))
):
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(current_user, "generer_rapports", rapport_data.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Vérifier que la période est valide
    if rapport_data.periode_fin < rapport_data.periode_debut:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La période de fin doit être postérieure à la période de début"
        )
    
    # Créer le rapport financier
    rapport = RapportFinancier(
        type_rapport=rapport_data.type_rapport,
        periode_debut=rapport_data.periode_debut,
        periode_fin=rapport_data.periode_fin,
        format_sortie=rapport_data.format_sortie,
        utilisateur_generateur_id=rapport_data.utilisateur_generateur_id or current_user.id,
        compagnie_id=rapport_data.compagnie_id,
        station_id=rapport_data.station_id,
        commentaire=rapport_data.commentaire
    )
    
    db.add(rapport)
    db.commit()
    db.refresh(rapport)
    
    return rapport

@router.get("/financiers/{rapport_id}", response_model=RapportFinancierResponse)
async def get_rapport_financier(
    rapport_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_rapports"))
):
    rapport = db.query(RapportFinancier).filter(
        RapportFinancier.id == rapport_id,
        RapportFinancier.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not rapport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport financier non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(current_user, "consulter_rapports", rapport.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    return rapport

@router.put("/financiers/{rapport_id}", response_model=RapportFinancierResponse)
async def update_rapport_financier(
    rapport_id: str,
    rapport_data: RapportFinancierUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_rapports"))
):
    rapport = db.query(RapportFinancier).filter(
        RapportFinancier.id == rapport_id,
        RapportFinancier.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not rapport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport financier non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(current_user, "gerer_rapports", rapport.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Mettre à jour les champs
    for field, value in rapport_data.dict(exclude_unset=True).items():
        setattr(rapport, field, value)
    
    db.commit()
    db.refresh(rapport)
    
    return rapport

@router.delete("/financiers/{rapport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rapport_financier(
    rapport_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_rapports"))
):
    rapport = db.query(RapportFinancier).filter(
        RapportFinancier.id == rapport_id,
        RapportFinancier.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not rapport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport financier non trouvé"
        )
    
    # Vérifier la permission
    if not check_user_permission(current_user, "gerer_rapports", rapport.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    db.delete(rapport)
    db.commit()
    
    return

@router.get("/financiers/", response_model=List[RapportFinancierResponse])
async def list_rapports_financiers(
    compagnie_id: str = None,
    type_rapport: str = None,
    periode_debut: date = None,
    periode_fin: date = None,
    statut: str = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_rapports"))
):
    query = db.query(RapportFinancier).filter(
        RapportFinancier.compagnie_id == (compagnie_id or current_user.compagnie_id)
    )
    
    # Vérifier la permission
    user_compagnie_id = compagnie_id or current_user.compagnie_id
    if not check_user_permission(current_user, "consulter_rapports", user_compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    if type_rapport:
        query = query.filter(RapportFinancier.type_rapport == type_rapport)
    
    if periode_debut:
        query = query.filter(RapportFinancier.periode_debut >= periode_debut)
    
    if periode_fin:
        query = query.filter(RapportFinancier.periode_fin <= periode_fin)
    
    if statut:
        query = query.filter(RapportFinancier.statut == statut)
    
    # Trier par date de création
    query = query.order_by(RapportFinancier.created_at.desc())
    
    rapports = query.all()
    return rapports

# Endpoints pour l'historique des rapports
@router.post("/historique/", response_model=HistoriqueRapportResponse, status_code=status.HTTP_201_CREATED)
async def create_historique_rapport(
    historique_data: HistoriqueRapportCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_historique_rapports"))
):
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(current_user, "gerer_historique_rapports", historique_data.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Vérifier que la période est valide
    if historique_data.periode_fin < historique_data.periode_debut:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La période de fin doit être postérieure à la période de début"
        )
    
    # Créer l'historique du rapport
    historique = HistoriqueRapport(
        nom_rapport=historique_data.nom_rapport,
        type_rapport=historique_data.type_rapport,
        periode_debut=historique_data.periode_debut,
        periode_fin=historique_data.periode_fin,
        utilisateur_demandeur_id=historique_data.utilisateur_demandeur_id or current_user.id,
        utilisateur_generation_id=historique_data.utilisateur_generation_id,
        compagnie_id=historique_data.compagnie_id,
        station_id=historique_data.station_id
    )
    
    db.add(historique)
    db.commit()
    db.refresh(historique)
    
    return historique

@router.get("/historique/", response_model=List[HistoriqueRapportResponse])
async def list_historique_rapports(
    compagnie_id: str = None,
    type_rapport: str = None,
    nom_rapport: str = None,
    periode_debut: date = None,
    periode_fin: date = None,
    statut: str = None,
    est_a_jour: bool = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_historique_rapports"))
):
    query = db.query(HistoriqueRapport).filter(
        HistoriqueRapport.compagnie_id == (compagnie_id or current_user.compagnie_id)
    )
    
    # Vérifier la permission
    user_compagnie_id = compagnie_id or current_user.compagnie_id
    if not check_user_permission(current_user, "consulter_historique_rapports", user_compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    if type_rapport:
        query = query.filter(HistoriqueRapport.type_rapport == type_rapport)
    
    if nom_rapport:
        query = query.filter(HistoriqueRapport.nom_rapport == nom_rapport)
    
    if periode_debut:
        query = query.filter(HistoriqueRapport.periode_debut >= periode_debut)
    
    if periode_fin:
        query = query.filter(HistoriqueRapport.periode_fin <= periode_fin)
    
    if statut:
        query = query.filter(HistoriqueRapport.statut == statut)
    
    if est_a_jour is not None:
        query = query.filter(HistoriqueRapport.est_a_jour == est_a_jour)
    
    # Trier par date de création
    query = query.order_by(HistoriqueRapport.created_at.desc())
    
    historiques = query.all()
    return historiques