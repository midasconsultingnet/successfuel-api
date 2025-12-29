from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from ...models import Achat as AchatModel, AchatDetail as AchatDetailModel
from ...achats import schemas
from ..tresorerie.mouvement_manager import MouvementTresorerieManager
from ..mouvement_stock_service import enregistrer_mouvement_stock
from datetime import datetime, timezone


def get_achats(db: Session, skip: int = 0, limit: int = 100):
    """Récupère la liste des achats avec pagination"""
    achats = db.query(AchatModel).offset(skip).limit(limit).all()
    return achats


def create_achat(db: Session, achat: schemas.AchatCreate, utilisateur_id: str = None):
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
        compagnie_id=achat.compagnie_id,
        tresorerie_station_id=achat.tresorerie_station_id
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

        # Enregistrer le mouvement de stock pour chaque détail d'achat
        try:
            enregistrer_mouvement_stock(
                db=db,
                produit_id=detail.produit_id,
                station_id=achat.station_id,
                type_mouvement="entree",
                quantite=detail.quantite_demandee,
                cout_unitaire=detail.prix_unitaire_demande,
                utilisateur_id=utilisateur_id,
                module_origine="achats_boutique",
                reference_origine=f"ACH-{db_achat.id}",
                transaction_source_id=str(db_achat.id),
                type_transaction_source="achat"
            )
        except Exception as e:
            # If stock movement creation fails, we should handle it appropriately
            # For now, we'll just log the error, but in a real application you might want to rollback
            print(f"Error creating stock movement for achat {db_achat.id}, product {detail.produit_id}: {str(e)}")

    db.commit()
    db.refresh(db_achat)

    # Create treasury movement for the purchase
    try:
        mouvement = MouvementTresorerieManager.creer_mouvement_achat(
            db=db,
            achat_id=db_achat.id,
            type_achat='boutique',
            utilisateur_id=utilisateur_id,
            montant=db_achat.montant_total,
            tresorerie_station_id=db_achat.tresorerie_station_id
        )
    except Exception as e:
        # If treasury movement creation fails, we should handle it appropriately
        # For now, we'll just log the error, but in a real application you might want to rollback
        print(f"Error creating treasury movement for achat {db_achat.id}: {str(e)}")

    return db_achat


def get_achat_by_id(db: Session, achat_id: int):
    """Récupère un achat spécifique par son ID"""
    achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat not found")
    return achat


def update_achat(db: Session, achat_id: int, achat: schemas.AchatUpdate):
    """Met à jour un achat existant"""
    from ..mouvement_stock_service import annuler_mouvements_stock_transaction

    db_achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not db_achat:
        raise HTTPException(status_code=404, detail="Achat not found")

    # Annuler les anciens mouvements de stock liés à cet achat
    try:
        annuler_mouvements_stock_transaction(
            db=db,
            transaction_source_id=str(achat_id),
            type_transaction_source="achat"
        )
    except Exception as e:
        # If stock movement cancellation fails, we should handle it appropriately
        # For now, we'll just log the error, but in a real application you might want to rollback
        print(f"Error cancelling stock movements for achat {achat_id}: {str(e)}")

    update_data = achat.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_achat, field, value)

    db.commit()
    db.refresh(db_achat)
    return db_achat


def delete_achat(db: Session, achat_id: int):
    """Supprime un achat existant"""
    from ..mouvement_stock_service import annuler_mouvements_stock_transaction

    achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat not found")

    # Annuler les mouvements de stock liés à cet achat
    try:
        annuler_mouvements_stock_transaction(
            db=db,
            transaction_source_id=str(achat_id),
            type_transaction_source="achat"
        )
    except Exception as e:
        # If stock movement cancellation fails, we should handle it appropriately
        # For now, we'll just log the error, but in a real application you might want to rollback
        print(f"Error cancelling stock movements for achat {achat_id}: {str(e)}")

    # Delete related details first
    db.query(AchatDetailModel).filter(AchatDetailModel.achat_id == str(achat_id)).delete()

    db.delete(achat)
    db.commit()
    return {"message": "Achat deleted successfully"}


def get_achat_details(db: Session, achat_id: int, skip: int = 0, limit: int = 100):
    """Récupère les détails d'un achat spécifique"""
    details = db.query(AchatDetailModel).filter(AchatDetailModel.achat_id == str(achat_id)).offset(skip).limit(limit).all()
    return details