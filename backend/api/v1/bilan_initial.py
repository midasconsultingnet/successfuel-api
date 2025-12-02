from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import date

from database.database import get_db
from models.comptabilite import (
    BilanInitial, BilanInitialLigne, ImmobilisationBilanInitial,
    StockBilanInitial, CreanceDetteBilanInitial, PlanComptable
)
from schemas.comptabilite import (
    BilanInitialCreate, BilanInitialUpdate, BilanInitialResponse, BilanInitialCreateRequest
)
from utils.access_control import require_permission, check_user_permission, create_permission_dependency
from models.structures import Utilisateur

router = APIRouter(tags=["Bilan Initial"])

@router.post("/", response_model=BilanInitialResponse, status_code=status.HTTP_201_CREATED)
async def create_bilan_initial(
    bilan_data: BilanInitialCreateRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_bilan_initial"))
):
    # Vérifier la permission pour la compagnie de l'utilisateur
    if not check_user_permission(db, current_user.id, "gerer_bilan_initial"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )

    # Vérifier que tous les comptes spécifiés existent et appartiennent à la bonne compagnie
    compte_ids = [ligne.compte_id for ligne in bilan_data.lignes if ligne.compte_id]
    if compte_ids:
        comptes = db.query(PlanComptable).filter(
            PlanComptable.id.in_(compte_ids),
            PlanComptable.compagnie_id == current_user.compagnie_id
        ).all()

        if len(comptes) != len(compte_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un ou plusieurs comptes spécifiés n'existent pas ou sont inaccessibles"
            )

    # Créer le bilan initial
    bilan = BilanInitial(
        compagnie_id=current_user.compagnie_id,
        date_bilan_initial=bilan_data.date_bilan_initial,
        commentaire=bilan_data.commentaire,
        utilisateur_id=bilan_data.utilisateur_id or current_user.id,
        description=bilan_data.description
    )
    
    db.add(bilan)
    db.flush()  # Pour obtenir l'ID du bilan avant de créer les lignes
    
    # Créer les lignes du bilan initial
    for ligne_data in bilan_data.lignes:
        ligne = BilanInitialLigne(
            bilan_initial_id=bilan.id,
            compte_numero=ligne_data.compte_numero,
            compte_id=ligne_data.compte_id,
            montant_initial=ligne_data.montant_initial,
            type_solde=ligne_data.type_solde,
            poste_bilan=ligne_data.poste_bilan,
            categorie_detaillee=ligne_data.categorie_detaillee,
            commentaire=ligne_data.commentaire
        )
        db.add(ligne)
    
    # Créer les immobilisations du bilan initial
    for immo_data in bilan_data.immobilisations:
        immo = ImmobilisationBilanInitial(
            bilan_initial_id=bilan.id,
            code=immo_data.code,
            libelle=immo_data.libelle,
            categorie=immo_data.categorie,
            date_achat=immo_data.date_achat,
            valeur_acquisition=immo_data.valeur_acquisition,
            valeur_nette_comptable=immo_data.valeur_nette_comptable,
            amortissement_cumule=immo_data.amortissement_cumule,
            duree_amortissement=immo_data.duree_amortissement,
            date_fin_amortissement=immo_data.date_fin_amortissement,
            fournisseur_id=immo_data.fournisseur_id,
            utilisateur_achat_id=immo_data.utilisateur_achat_id,
            observation=immo_data.observation,
            statut=immo_data.statut
        )
        db.add(immo)
    
    # Créer les stocks du bilan initial
    for stock_data in bilan_data.stocks:
        stock = StockBilanInitial(
            bilan_initial_id=bilan.id,
            type_stock=stock_data.type_stock,
            article_id=stock_data.article_id,
            carburant_id=stock_data.carburant_id,
            cuve_id=stock_data.cuve_id,
            quantite=stock_data.quantite,
            prix_unitaire=stock_data.prix_unitaire,
            commentaire=stock_data.commentaire
        )
        db.add(stock)
    
    # Créer les créances/dettes du bilan initial
    for cd_data in bilan_data.creances_dettes:
        cd = CreanceDetteBilanInitial(
            bilan_initial_id=bilan.id,
            type_tiers=cd_data.type_tiers,
            tiers_id=cd_data.tiers_id,
            montant_initial=cd_data.montant_initial,
            devise=cd_data.devise,
            date_echeance=cd_data.date_echeance,
            reference_piece=cd_data.reference_piece,
            commentaire=cd_data.commentaire
        )
        db.add(cd)
    
    # Vérifier la cohérence du bilan (actif = passif + capitaux propres)
    total_actifs = db.query(func.sum(BilanInitialLigne.montant_initial)).filter(
        BilanInitialLigne.bilan_initial_id == bilan.id,
        BilanInitialLigne.poste_bilan == 'actif'
    ).scalar() or 0
    
    total_passif_capitaux = db.query(func.sum(BilanInitialLigne.montant_initial)).filter(
        BilanInitialLigne.bilan_initial_id == bilan.id,
        BilanInitialLigne.poste_bilan.in_(['passif', 'capitaux_propres'])
    ).scalar() or 0
    
    if abs(total_actifs - total_passif_capitaux) > 0.01:  # Tolérance pour les arrondis
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le bilan n'est pas équilibré: actif {total_actifs} != passif + capitaux propres {total_passif_capitaux}"
        )
    
    db.commit()
    db.refresh(bilan)
    
    # Recharger le bilan avec ses relations
    bilan = db.query(BilanInitial).filter(BilanInitial.id == bilan.id).first()
    
    return bilan

@router.get("/{bilan_id}", response_model=BilanInitialResponse)
async def get_bilan_initial(
    bilan_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_bilan_initial"))
):
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
    if not check_user_permission(db, current_user.id, "consulter_bilan_initial"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    return bilan

@router.put("/{bilan_id}", response_model=BilanInitialResponse)
async def update_bilan_initial(
    bilan_id: str,
    bilan_data: BilanInitialUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_bilan_initial"))
):
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
    if not check_user_permission(db, current_user.id, "gerer_bilan_initial"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Ne permettre la modification que si le bilan n'est pas validé
    if bilan.est_valide:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de modifier un bilan déjà validé"
        )
    
    # Mettre à jour les champs
    for field, value in bilan_data.dict(exclude_unset=True).items():
        setattr(bilan, field, value)
    
    db.commit()
    db.refresh(bilan)
    
    return bilan

@router.delete("/{bilan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bilan_initial(
    bilan_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("gerer_bilan_initial"))
):
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
    if not check_user_permission(db, current_user.id, "gerer_bilan_initial"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    # Ne permettre la suppression que si le bilan n'est pas validé
    if bilan.est_valide:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer un bilan déjà validé"
        )
    
    db.delete(bilan)
    db.commit()
    
    return

@router.get("/", response_model=List[BilanInitialResponse])
async def list_bilan_initial(
    date_bilan: date = None,
    est_valide: bool = None,
    est_verifie: bool = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(create_permission_dependency("consulter_bilan_initial"))
):
    query = db.query(BilanInitial).filter(
        BilanInitial.compagnie_id == current_user.compagnie_id
    )

    # Vérifier la permission
    if not check_user_permission(db, current_user.id, "consulter_bilan_initial"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits nécessaires pour cette opération"
        )
    
    if date_bilan:
        query = query.filter(BilanInitial.date_bilan_initial == date_bilan)
    
    if est_valide is not None:
        query = query.filter(BilanInitial.est_valide == est_valide)
    
    if est_verifie is not None:
        query = query.filter(BilanInitial.est_verifie == est_verifie)
    
    # Trier par date de création
    query = query.order_by(BilanInitial.created_at.desc())
    
    bilans = query.all()
    return bilans