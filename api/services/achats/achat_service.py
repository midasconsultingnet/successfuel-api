from sqlalchemy.orm import Session
import uuid
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
    # Get the user to retrieve their company ID
    from ...models.user import User
    user = db.query(User).filter(User.id == utilisateur_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Calculate total amount from details
    total_amount = sum(detail.montant for detail in achat.details)

    # Create the main achat record
    db_achat = AchatModel(
        fournisseur_id=achat.fournisseur_id,
        station_id=achat.station_id,
        tresorerie_id=achat.tresorerie_id,
        date=achat.date,
        informations=achat.informations,
        montant_total=str(total_amount),  # Convert to string to match DECIMAL type
        statut="valide",  # Default status is now "valide"
        type_paiement=achat.type_paiement,
        delai_paiement=achat.delai_paiement,
        mode_reglement=achat.mode_reglement,
        compagnie_id=user.compagnie_id,
        date_livraison_prevue=None  # Will be set if provided in informations
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
        # Determine if tresorerie_id is a station treasury or global treasury
        from ...models.tresorerie import Tresorerie, TresorerieStation
        station_tresorerie = db.query(TresorerieStation).filter(TresorerieStation.id == achat.tresorerie_id).first()

        if station_tresorerie:
            # It's a station treasury
            mouvement = MouvementTresorerieManager.creer_mouvement_achat(
                db=db,
                achat_id=db_achat.id,
                type_achat='boutique',
                utilisateur_id=utilisateur_id,
                montant=db_achat.montant_total,
                tresorerie_station_id=achat.tresorerie_id
            )
        else:
            # Check if it's a global treasury
            global_tresorerie = db.query(Tresorerie).filter(Tresorerie.id == achat.tresorerie_id).first()
            if global_tresorerie:
                # For global treasury, we need to create the movement differently
                # We'll use the creer_mouvement_general method which supports tresorerie_globale_id
                mouvement = MouvementTresorerieManager.creer_mouvement_general(
                    db=db,
                    type_mouvement="sortie",  # Achat is a sortie from treasury
                    montant=db_achat.montant_total,
                    utilisateur_id=utilisateur_id,
                    description=f"Paiement pour achat boutique {db_achat.id}",
                    module_origine="achats_boutique",
                    reference_origine=f"AB-{db_achat.id}",
                    tresorerie_globale_id=achat.tresorerie_id,  # Using the global treasury ID
                    station_id=None  # Not using station_id in this case
                )
            else:
                # If the ID doesn't match either type, raise an error
                raise HTTPException(status_code=400, detail="L'ID de trésorerie fourni n'est ni une trésorerie station ni une trésorerie globale")
    except Exception as e:
        # If treasury movement creation fails, we should handle it appropriately
        # For now, we'll just log the error, but in a real application you might want to rollback
        print(f"Error creating treasury movement for achat {db_achat.id}: {str(e)}")

    return db_achat


def annuler_achat(db: Session, achat_id: int, utilisateur_id: uuid.UUID):
    """Annule un achat boutique en effectuant des écritures inverses pour le stock et la trésorerie"""
    from ..mouvement_stock_service import annuler_mouvements_stock_transaction
    from ..tresorerie.mouvement_manager import MouvementTresorerieManager
    from ...models.tresorerie import MouvementTresorerie
    from sqlalchemy import and_

    # Récupérer l'achat
    achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat non trouvé")

    # Vérifier que l'achat peut être annulé (par exemple, qu'il n'est pas déjà annulé)
    if achat.statut == "annule":
        raise HTTPException(status_code=400, detail="L'achat est déjà annulé")

    # Annuler les mouvements de stock liés à cet achat
    try:
        annuler_mouvements_stock_transaction(
            db=db,
            reference_origine=f"AB-{achat_id}",
            utilisateur_id=utilisateur_id
        )
    except Exception as e:
        print(f"Erreur lors de l'annulation des mouvements de stock pour l'achat {achat_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation des mouvements de stock")

    # Annuler les mouvements de trésorerie liés à cet achat
    try:
        # Trouver les mouvements de trésorerie liés à cet achat
        mouvements = db.query(MouvementTresorerie).filter(
            MouvementTresorerie.reference_origine == f"AB-{achat_id}"
        ).all()

        for mouvement in mouvements:
            # Créer un mouvement inverse pour annuler le mouvement existant
            mouvement_inverse = MouvementTresorerie(
                tresorerie_station_id=mouvement.tresorerie_station_id,
                tresorerie_globale_id=mouvement.tresorerie_globale_id,
                station_id=mouvement.station_id,
                type_mouvement="entree" if mouvement.type_mouvement == "sortie" else "sortie",  # Inverser le type
                montant=mouvement.montant,
                date_mouvement=datetime.utcnow(),
                description=f"Annulation - {mouvement.description}",
                module_origine=mouvement.module_origine,
                reference_origine=f"ANN-{mouvement.reference_origine}",  # Préfixe pour les annulations
                utilisateur_id=utilisateur_id
            )

            db.add(mouvement_inverse)

            # Annuler le mouvement original
            mouvement.est_actif = False

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'annulation des mouvements de trésorerie pour l'achat {achat_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation des mouvements de trésorerie")

    # Mettre à jour le statut de l'achat
    achat.statut = "annule"
    achat.date_modification = datetime.utcnow()

    db.commit()
    db.refresh(achat)

    return achat


def get_achat_by_id(db: Session, achat_id: uuid.UUID):
    """Récupère un achat spécifique par son ID"""
    achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat not found")
    return achat


def update_achat(db: Session, achat_id: int, achat: schemas.AchatUpdate, utilisateur_id: uuid.UUID):
    """Met à jour un achat existant"""
    from ..mouvement_stock_service import annuler_mouvements_stock_transaction
    from ..tresorerie.mouvement_manager import MouvementTresorerieManager
    from ...models.tresorerie import MouvementTresorerie
    from ...models.achat_detail import AchatDetail
    from sqlalchemy import and_

    db_achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not db_achat:
        raise HTTPException(status_code=404, detail="Achat not found")

    # Récupérer les anciens détails de l'achat avant modification
    anciens_details = db.query(AchatDetail).filter(AchatDetail.achat_id == achat_id).all()

    # Annuler les anciens mouvements de stock liés à cet achat
    try:
        annuler_mouvements_stock_transaction(
            db=db,
            reference_origine=f"AB-{achat_id}",
            utilisateur_id=utilisateur_id
        )
    except Exception as e:
        # Gérer l'erreur d'annulation des mouvements de stock
        print(f"Erreur lors de l'annulation des mouvements de stock pour l'achat {achat_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation des mouvements de stock")

    # Annuler les anciens mouvements de trésorerie liés à cet achat
    try:
        # Trouver les mouvements de trésorerie liés à cet achat
        mouvements = db.query(MouvementTresorerie).filter(
            MouvementTresorerie.reference_origine == f"AB-{achat_id}"
        ).all()

        for mouvement in mouvements:
            # Créer un mouvement inverse pour annuler le mouvement existant
            mouvement_inverse = MouvementTresorerie(
                tresorerie_station_id=mouvement.tresorerie_station_id,
                tresorerie_globale_id=mouvement.tresorerie_globale_id,
                station_id=mouvement.station_id,
                type_mouvement="entree" if mouvement.type_mouvement == "sortie" else "sortie",  # Inverser le type
                montant=mouvement.montant,
                date_mouvement=datetime.utcnow(),
                description=f"Correction - Annulation de l'ancien mouvement pour mise à jour de l'achat {achat_id}",
                module_origine=mouvement.module_origine,
                reference_origine=f"COR-{mouvement.reference_origine}",  # Préfixe pour les corrections
                utilisateur_id=utilisateur_id
            )

            db.add(mouvement_inverse)

            # Marquer le mouvement original comme inactif
            mouvement.est_actif = False

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'annulation des mouvements de trésorerie pour l'achat {achat_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation des mouvements de trésorerie")

    # Mettre à jour les champs de base de l'achat
    update_data = achat.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "informations":
            setattr(db_achat, field, value)
        else:
            # Gérer la mise à jour du champ JSONB 'informations'
            if db_achat.informations is None:
                db_achat.informations = {}
            db_achat.informations.update(value)

    # IMPORTANT: Pour une mise à jour complète, il faudrait ici récupérer les nouveaux détails
    # et recréer les mouvements de stock et de trésorerie en conséquence
    # Cela dépend de la façon dont les détails sont transmis dans le schéma AchatUpdate

    db.commit()
    db.refresh(db_achat)

    return db_achat


def delete_achat(db: Session, achat_id: uuid.UUID):
    """Supprime un achat existant"""
    from ..mouvement_stock_service import annuler_mouvements_stock_transaction

    achat = db.query(AchatModel).filter(AchatModel.id == achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat not found")

    # Annuler les mouvements de stock liés à cet achat
    try:
        annuler_mouvements_stock_transaction(
            db=db,
            reference_origine=f"AB-{achat_id}",
            utilisateur_id=achat.utilisateur_id  # Utiliser l'utilisateur associé à l'achat
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
    """Récupère les détails d'un achat spécifique avec les informations complètes sur les produits"""
    from sqlalchemy.orm import joinedload

    details = db.query(AchatDetailModel).options(
        joinedload(AchatDetailModel.produit)
    ).filter(AchatDetailModel.achat_id == str(achat_id)).offset(skip).limit(limit).all()

    return details


def corriger_achat_detail(db: Session, detail_id: uuid.UUID, correction_data: dict, utilisateur_id: uuid.UUID):
    """Corrige une ligne de détail d'achat suite à une erreur de saisie"""
    from ..mouvement_stock_service import annuler_mouvements_stock_transaction, enregistrer_mouvement_stock
    from ..tresorerie.mouvement_manager import MouvementTresorerieManager
    from ...models.tresorerie import MouvementTresorerie
    from sqlalchemy import and_
    from datetime import datetime

    # Récupérer le détail de l'achat
    detail = db.query(AchatDetailModel).filter(AchatDetailModel.id == detail_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Détail d'achat non trouvé")

    # Récupérer l'achat principal
    achat = db.query(AchatModel).filter(AchatModel.id == detail.achat_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat principal non trouvé")

    from decimal import Decimal

    # Calculer les anciennes et nouvelles valeurs
    ancienne_valeur = Decimal(str(detail.quantite_demandee)) * Decimal(str(detail.prix_unitaire_demande))
    nouvelle_quantite = correction_data.get('nouvelle_quantite', detail.quantite_demandee)
    nouveau_prix = correction_data.get('nouveau_prix_unitaire', detail.prix_unitaire_demande)
    nouvelle_valeur = Decimal(str(nouvelle_quantite)) * Decimal(str(nouveau_prix))

    # Annuler les mouvements de stock liés à ce détail
    try:
        annuler_mouvements_stock_transaction(
            db=db,
            transaction_source_id=str(achat.id),
            type_transaction_source="achat"
        )
    except Exception as e:
        print(f"Erreur lors de l'annulation des mouvements de stock pour le détail {detail_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation des mouvements de stock")

    # Annuler les mouvements de trésorerie liés à ce détail
    try:
        # Trouver les mouvements de trésorerie liés à ce détail
        mouvements = db.query(MouvementTresorerie).filter(
            MouvementTresorerie.reference_origine == f"AB-{achat.id}-D{detail.id}"
        ).all()

        for mouvement in mouvements:
            # Créer un mouvement inverse pour annuler le mouvement existant
            mouvement_inverse = MouvementTresorerie(
                tresorerie_station_id=mouvement.tresorerie_station_id,
                tresorerie_globale_id=mouvement.tresorerie_globale_id,
                station_id=mouvement.station_id,
                type_mouvement="entree" if mouvement.type_mouvement == "sortie" else "sortie",  # Inverser le type
                montant=mouvement.montant,
                date_mouvement=datetime.utcnow(),
                description=f"Correction - Annulation de l'ancien mouvement pour mise à jour du détail {detail.id}",
                module_origine=mouvement.module_origine,
                reference_origine=f"COR-{mouvement.reference_origine}",  # Préfixe pour les corrections
                utilisateur_id=utilisateur_id
            )

            db.add(mouvement_inverse)

            # Marquer le mouvement original comme inactif
            mouvement.est_actif = False

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'annulation des mouvements de trésorerie pour le détail {detail_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation des mouvements de trésorerie")

    # Mettre à jour le détail de l'achat
    detail.quantite_demandee = nouvelle_quantite
    detail.prix_unitaire_demande = nouveau_prix
    detail.montant = float(nouvelle_valeur)  # Convertir en float pour correspondre au type dans le modèle
    detail.date_modification = datetime.utcnow()

    # Mettre à jour le montant total de l'achat
    achat.montant_total = str(Decimal(achat.montant_total) - ancienne_valeur + nouvelle_valeur)
    achat.date_modification = datetime.utcnow()

    # Enregistrer le nouveau mouvement de stock
    try:
        enregistrer_mouvement_stock(
            db=db,
            produit_id=detail.produit_id,
            station_id=achat.station_id,
            type_mouvement="entree",
            quantite=nouvelle_quantite,
            cout_unitaire=nouveau_prix,
            utilisateur_id=utilisateur_id,
            module_origine="achats_boutique",
            reference_origine=f"AB-{achat.id}-D{detail.id}",  # Référence spécifique au détail
            transaction_source_id=str(achat.id),
            type_transaction_source="achat"
        )
    except Exception as e:
        print(f"Erreur lors de la création du nouveau mouvement de stock pour le détail {detail_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du nouveau mouvement de stock")

    # Créer un nouveau mouvement de trésorerie pour la différence
    try:
        # Déterminer si la trésorerie est une trésorerie station ou globale
        from ...models.tresorerie import Tresorerie, TresorerieStation
        station_tresorerie = db.query(TresorerieStation).filter(TresorerieStation.id == achat.tresorerie_id).first()

        if station_tresorerie:
            # C'est une trésorerie station
            mouvement = MouvementTresorerieManager.creer_mouvement_general(
                db=db,
                type_mouvement="sortie",  # L'achat est une sortie de trésorerie
                montant=float(abs(nouvelle_valeur - ancienne_valeur)),
                utilisateur_id=utilisateur_id,
                description=f"Correction pour achat boutique détail {detail.id}",
                module_origine="achats_boutique",
                reference_origine=f"AB-{achat.id}-D{detail.id}",
                tresorerie_station_id=achat.tresorerie_id
            )
        else:
            # Vérifier si c'est une trésorerie globale
            global_tresorerie = db.query(Tresorerie).filter(Tresorerie.id == achat.tresorerie_id).first()
            if global_tresorerie:
                # Pour la trésorerie globale, créer le mouvement différemment
                mouvement = MouvementTresorerieManager.creer_mouvement_general(
                    db=db,
                    type_mouvement="sortie",  # L'achat est une sortie de trésorerie
                    montant=float(abs(nouvelle_valeur - ancienne_valeur)),
                    utilisateur_id=utilisateur_id,
                    description=f"Correction pour achat boutique détail {detail.id}",
                    module_origine="achats_boutique",
                    reference_origine=f"AB-{achat.id}-D{detail.id}",
                    tresorerie_globale_id=achat.tresorerie_id  # Utiliser l'ID de la trésorerie globale
                )
            else:
                # Si ce n'est ni une trésorerie station ni globale, on tente avec le station_id
                # Cela pourrait être un mouvement lié directement à une station
                mouvement = MouvementTresorerieManager.creer_mouvement_general(
                    db=db,
                    type_mouvement="sortie",  # L'achat est une sortie de trésorerie
                    montant=float(abs(nouvelle_valeur - ancienne_valeur)),
                    utilisateur_id=utilisateur_id,
                    description=f"Correction pour achat boutique détail {detail.id}",
                    module_origine="achats_boutique",
                    reference_origine=f"AB-{achat.id}-D{detail.id}",
                    station_id=achat.station_id  # Utiliser l'ID de la station
                )
    except Exception as e:
        print(f"Erreur lors de la création du nouveau mouvement de trésorerie pour le détail {detail_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du nouveau mouvement de trésorerie")

    db.commit()
    db.refresh(detail)
    db.refresh(achat)

    return detail