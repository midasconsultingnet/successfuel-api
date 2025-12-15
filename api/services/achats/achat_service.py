from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from ...models import Achat as AchatModel, AchatDetail as AchatDetailModel
from ...achats import schemas


def get_achats(db: Session, skip: int = 0, limit: int = 100):
    """Récupère la liste des achats avec pagination"""
    achats = db.query(AchatModel).offset(skip).limit(limit).all()
    return achats


def create_achat(db: Session, achat: schemas.AchatCreate):
    """Crée un nouvel achat avec ses détails"""
    # Calculate total amount from details
    total_amount = sum(detail.montant for detail in achat.details)

    # Create the main achat record
    db_achat = AchatModel(
        fournisseur_id=achat.fournisseur_id,
        station_id=achat.station_id,
        date=achat.date,
        numero_bl=achat.numero_bl,
        numero_facture=achat.numero_facture,
        date_facturation=achat.date_facturation,
        montant_total=total_amount,
        statut="brouillon",  # Default status
        type_paiement=achat.type_paiement,
        delai_paiement=achat.delai_paiement,
        pourcentage_acompte=achat.pourcentage_acompte,
        limite_credit=achat.limite_credit,
        mode_reglement=achat.mode_reglement,
        documents_requis=achat.documents_requis,
        compagnie_id=achat.compagnie_id
    )

    db.add(db_achat)
    db.flush()  # To get the ID before committing

    # Create the details
    for detail in achat.details:
        db_detail = AchatDetailModel(
            achat_id=str(db_achat.id),
            produit_id=detail.produit_id,
            quantite_demandee=detail.quantite_demandee,
            prix_unitaire_demande=detail.prix_unitaire_demande,
            montant=detail.montant
        )
        db.add(db_detail)

    db.commit()
    db.refresh(db_achat)

    return db_achat


def get_achat_by_id(db: Session, achat_id: int):
    """Récupère un achat spécifique par son ID"""
    achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat not found")
    return achat


def update_achat(db: Session, achat_id: int, achat: schemas.AchatUpdate):
    """Met à jour un achat existant"""
    db_achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not db_achat:
        raise HTTPException(status_code=404, detail="Achat not found")

    update_data = achat.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_achat, field, value)

    db.commit()
    db.refresh(db_achat)
    return db_achat


def delete_achat(db: Session, achat_id: int):
    """Supprime un achat existant"""
    achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat not found")

    # Delete related details first
    db.query(AchatDetailModel).filter(AchatDetailModel.achat_id == str(achat_id)).delete()

    db.delete(achat)
    db.commit()
    return {"message": "Achat deleted successfully"}


def get_achat_details(db: Session, achat_id: int, skip: int = 0, limit: int = 100):
    """Récupère les détails d'un achat spécifique"""
    details = db.query(AchatDetailModel).filter(AchatDetailModel.achat_id == str(achat_id)).offset(skip).limit(limit).all()
    return details