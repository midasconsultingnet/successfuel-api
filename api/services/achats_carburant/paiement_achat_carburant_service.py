"""
Service pour la gestion des paiements des achats de carburant.

Ce module contient les fonctions pour créer, lire, mettre à jour et supprimer
des paiements d'achats de carburant dans l'application Succès Fuel.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ...models import PaiementAchatCarburant as PaiementAchatCarburantModel
from ...achats_carburant import schemas
from ...services.tiers.tiers_solde_service import (
    mettre_a_jour_solde_apres_paiement,
    valider_montant_paiements_achat,
    calculer_solde_achat
)
from ...services.tresoreries.validation_service import valider_paiement_achat_carburant


def create_paiement_achat_carburant(
    db: Session,
    paiement: schemas.PaiementAchatCarburantCreate
) -> PaiementAchatCarburantModel:
    """
    Crée un nouveau paiement pour un achat de carburant.

    Args:
        db (Session): Session de base de données
        paiement (schemas.PaiementAchatCarburantCreate): Détails du paiement à créer

    Returns:
        PaiementAchatCarburantModel: Le paiement d'achat de carburant créé
    """
    # Valider que le montant du paiement est cohérent avec le solde de l'achat
    solde_achat = calculer_solde_achat(db, paiement.achat_carburant_id)

    if solde_achat > 0 and paiement.montant > solde_achat:
        raise ValueError(f"Le montant du paiement ({paiement.montant}) dépasse le solde restant de l'achat ({solde_achat})")

    # Valider que la trésorerie a suffisamment de fonds pour le paiement
    valider_paiement_achat_carburant(
        db,
        paiement.tresorerie_station_id,
        paiement.montant
    )

    db_paiement = PaiementAchatCarburantModel(
        achat_carburant_id=paiement.achat_carburant_id,
        date_paiement=paiement.date_paiement,
        montant=paiement.montant,
        mode_paiement=paiement.mode_paiement,
        tresorerie_station_id=paiement.tresorerie_station_id,
    )

    db.add(db_paiement)
    db.commit()
    db.refresh(db_paiement)

    # Mettre à jour le solde du fournisseur après le paiement
    mettre_a_jour_solde_apres_paiement(
        db=db,
        achat_id=paiement.achat_carburant_id,
        utilisateur_id=paiement.utilisateur_id
    )

    return db_paiement


def get_paiement_achat_carburant(
    db: Session,
    paiement_id: UUID
) -> Optional[PaiementAchatCarburantModel]:
    """
    Récupère un paiement d'achat de carburant par son identifiant.

    Args:
        db (Session): Session de base de données
        paiement_id (UUID): Identifiant du paiement à récupérer

    Returns:
        Optional[PaiementAchatCarburantModel]: Le paiement d'achat de carburant trouvé ou None
    """
    return db.query(PaiementAchatCarburantModel).filter(
        PaiementAchatCarburantModel.id == paiement_id
    ).first()


def get_paiements_achat_carburant(
    db: Session,
    achat_carburant_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[PaiementAchatCarburantModel]:
    """
    Récupère la liste des paiements pour un achat de carburant spécifique.

    Args:
        db (Session): Session de base de données
        achat_carburant_id (UUID): Identifiant de l'achat pour lequel récupérer les paiements
        skip (int): Nombre de paiements à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de paiements à retourner (défaut: 100)

    Returns:
        List[PaiementAchatCarburantModel]: Liste des paiements d'achat de carburant
    """
    return db.query(PaiementAchatCarburantModel).filter(
        PaiementAchatCarburantModel.achat_carburant_id == achat_carburant_id
    ).offset(skip).limit(limit).all()


def update_paiement_achat_carburant(
    db: Session,
    paiement_id: UUID,
    paiement: schemas.PaiementAchatCarburantUpdate
) -> Optional[PaiementAchatCarburantModel]:
    """
    Met à jour les détails d'un paiement d'achat de carburant existant.

    Args:
        db (Session): Session de base de données
        paiement_id (UUID): Identifiant du paiement à mettre à jour
        paiement (schemas.PaiementAchatCarburantUpdate): Nouvelles données du paiement

    Returns:
        Optional[PaiementAchatCarburantModel]: Le paiement mis à jour ou None s'il n'existe pas
    """
    db_paiement = db.query(PaiementAchatCarburantModel).filter(
        PaiementAchatCarburantModel.id == paiement_id
    ).first()

    if not db_paiement:
        return None

    # Sauvegarder les anciennes valeurs pour référence
    achat_id_original = db_paiement.achat_carburant_id
    utilisateur_id_original = db_paiement.utilisateur_enregistrement_id
    montant_original = db_paiement.montant
    tresorerie_station_id_original = db_paiement.tresorerie_station_id

    # Si le montant est mis à jour, valider le nouveau montant
    if paiement.montant is not None:
        # Calculer le solde restant de l'achat avant le changement
        solde_achat = calculer_solde_achat(db, achat_id_original)

        # Calculer la différence entre ancien et nouveau montant
        difference_montant = paiement.montant - montant_original

        # Vérifier si le nouveau montant dépasse le solde restant
        if solde_achat > 0 and (solde_achat - difference_montant) < 0:
            raise ValueError(f"Le nouveau montant du paiement ({paiement.montant}) dépasse le solde restant de l'achat ({solde_achat})")

    # Si le montant ou la trésorerie station est mis à jour, valider que la trésorerie a suffisamment de fonds
    nouveau_montant = paiement.montant if paiement.montant is not None else montant_original
    nouvelle_tresorerie_station = paiement.tresorerie_station_id if paiement.tresorerie_station_id is not None else tresorerie_station_id_original

    if paiement.montant is not None or paiement.tresorerie_station_id is not None:
        valider_paiement_achat_carburant(
            db,
            nouvelle_tresorerie_station,
            nouveau_montant
        )

    update_data = paiement.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_paiement, field, value)

    db.commit()
    db.refresh(db_paiement)

    # Mettre à jour le solde du fournisseur après la modification du paiement
    # Utiliser les données originales pour déterminer quel achat mettre à jour
    mettre_a_jour_solde_apres_paiement(
        db=db,
        achat_id=achat_id_original,
        utilisateur_id=utilisateur_id_original
    )

    return db_paiement


def delete_paiement_achat_carburant(
    db: Session,
    paiement_id: UUID
) -> bool:
    """
    Supprime un paiement d'achat de carburant existant.

    Args:
        db (Session): Session de base de données
        paiement_id (UUID): Identifiant du paiement à supprimer

    Returns:
        bool: True si le paiement a été supprimé, False s'il n'existait pas
    """
    db_paiement = db.query(PaiementAchatCarburantModel).filter(
        PaiementAchatCarburantModel.id == paiement_id
    ).first()

    if not db_paiement:
        return False

    # Sauvegarder les valeurs pour référence avant la suppression
    achat_id_original = db_paiement.achat_carburant_id
    utilisateur_id_original = db_paiement.utilisateur_id

    db.delete(db_paiement)
    db.commit()

    # Mettre à jour le solde du fournisseur après la suppression du paiement
    mettre_a_jour_solde_apres_paiement(
        db=db,
        achat_id=achat_id_original,
        utilisateur_id=utilisateur_id_original
    )

    return True