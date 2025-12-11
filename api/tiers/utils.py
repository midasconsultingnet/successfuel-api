from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..models.tiers import MouvementTiers, SoldeTiers
from decimal import Decimal
import uuid

def calculer_solde_actuel(db: Session, tiers_id: uuid.UUID) -> float:
    """
    Calcule le solde actuel d'un tiers en se basant sur le montant initial
    et sur tous les mouvements (crédits et débits) enregistrés.

    Args:
        db: Session SQLAlchemy
        tiers_id: UUID du tiers pour lequel on calcule le solde

    Returns:
        float: Le solde actuel du tiers
    """
    # Récupérer le solde initial
    solde_initial = db.query(SoldeTiers.montant_initial).filter(
        SoldeTiers.tiers_id == tiers_id
    ).scalar()

    if solde_initial is None:
        # Si aucun solde initial n'existe, on retourne 0
        return 0.0

    # Calculer la somme des crédits et des débits
    mouvements = db.query(
        func.sum(
            case(
                (MouvementTiers.type_mouvement == 'crédit', MouvementTiers.montant),
                else_=0
            )
        ).label('total_credits'),
        func.sum(
            case(
                (MouvementTiers.type_mouvement == 'débit', MouvementTiers.montant),
                else_=0
            )
        ).label('total_debits')
    ).filter(
        MouvementTiers.tiers_id == tiers_id,
        MouvementTiers.statut == 'validé'  # Ne prendre en compte que les mouvements validés
    ).first()

    total_credits = float(mouvements[0] or 0)
    total_debits = float(mouvements[1] or 0)

    # Calculer le solde actuel
    solde_actuel = float(solde_initial) + total_credits - total_debits

    return solde_actuel

def mettre_a_jour_solde_actuel(db: Session, tiers_id: uuid.UUID) -> float:
    """
    Met à jour le montant_actuel dans la table SoldeTiers en fonction
    du montant initial et des mouvements enregistrés.

    Args:
        db: Session SQLAlchemy
        tiers_id: UUID du tiers à mettre à jour

    Returns:
        float: Le nouveau solde actuel
    """
    nouveau_solde = calculer_solde_actuel(db, tiers_id)

    # Mettre à jour le montant_actuel dans SoldeTiers
    solde_tiers = db.query(SoldeTiers).filter(SoldeTiers.tiers_id == tiers_id).first()

    if solde_tiers:
        solde_tiers.montant_actuel = Decimal(str(nouveau_solde))
        db.commit()
        db.refresh(solde_tiers)

    return nouveau_solde

def determiner_statut_tiers(db: Session, tiers_id: uuid.UUID) -> str:
    """
    Détermine le statut d'un tiers en fonction de sa situation financière.

    Args:
        db: Session SQLAlchemy
        tiers_id: UUID du tiers

    Returns:
        str: Le statut ('actif', 'inactif', 'supprimé')
    """
    from ..models.tiers import SoldeTiers, MouvementTiers, Tiers

    # Vérifier si le tiers est marqué comme supprimé
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
    if not tiers or tiers.statut == "supprimé":
        return "supprimé"

    # Vérifier s'il existe un solde initial
    solde_initial = db.query(SoldeTiers).filter(SoldeTiers.tiers_id == tiers_id).first()

    if solde_initial:
        return "actif"
    else:
        return "inactif"

def mettre_a_jour_statut_tiers(db: Session, tiers_id: uuid.UUID) -> str:
    """
    Met à jour le statut d'un tiers dans la base de données.

    Args:
        db: Session SQLAlchemy
        tiers_id: UUID du tiers

    Returns:
        str: Le nouveau statut
    """
    from ..models.tiers import Tiers

    nouveau_statut = determiner_statut_tiers(db, tiers_id)

    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
    if tiers:
        tiers.statut = nouveau_statut
        db.commit()
        db.refresh(tiers)

    return tiers.statut if tiers else nouveau_statut