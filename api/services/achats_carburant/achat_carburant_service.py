from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ...models.achat_carburant import AchatCarburant, LigneAchatCarburant, PaiementAchatCarburant
from ...models.operation_journal import OperationJournal
from ...achats_carburant.schemas import (
    AchatCarburantCreateWithDetails,
    AchatCarburantDetailCreate,
    AchatCarburantReglementCreate
)
from ...services.tiers.tiers_solde_service import (
    mettre_a_jour_solde_apres_achat,
    mettre_a_jour_solde_fournisseur,
    calculer_solde_achat
)
from ...services.tresoreries.validation_service import valider_paiement_achat_carburant
import uuid
from datetime import datetime


def create_achat_carburant_complet(
    db: Session,
    achat_data: AchatCarburantCreateWithDetails,
    utilisateur_id: UUID
) -> AchatCarburant:
    """
    Créer un achat de carburant avec ses détails et ses paiements.

    Args:
        db: Session de base de données
        achat_data: Données de l'achat avec détails et paiements
        utilisateur_id: ID de l'utilisateur effectuant l'opération

    Returns:
        AchatCarburant: L'achat créé avec ses relations
    """
    try:
        # Vérifier que le fournisseur existe
        from ...models.tiers import Tiers
        fournisseur = db.query(Tiers).filter(
            Tiers.id == achat_data.fournisseur_id,
            Tiers.type == 'fournisseur'
        ).first()

        if not fournisseur:
            raise ValueError(f"Fournisseur avec l'ID {achat_data.fournisseur_id} non trouvé")

        # Récupérer la compagnie de l'utilisateur connecté
        from ...models.user import User
        utilisateur = db.query(User).filter(User.id == utilisateur_id).first()
        if not utilisateur:
            raise ValueError(f"Utilisateur avec l'ID {utilisateur_id} non trouvé")

        # Créer l'achat principal
        achat = AchatCarburant(
            fournisseur_id=achat_data.fournisseur_id,
            date_achat=achat_data.date_achat,
            autres_infos={"numero_bl": achat_data.numero_bl} if achat_data.numero_bl else None,
            numero_facture=achat_data.numero_facture,
            montant_total=achat_data.montant_total,
            compagnie_id=utilisateur.compagnie_id,  # Récupérer automatiquement la compagnie de l'utilisateur
            utilisateur_id=utilisateur_id
        )
        db.add(achat)
        db.flush()  # Pour obtenir l'ID

        # Créer les détails de l'achat
        for detail in achat_data.details:
            ligne = LigneAchatCarburant(
                achat_carburant_id=achat.id,
                carburant_id=detail.carburant_id,
                quantite=detail.quantite,
                prix_unitaire=0,  # À calculer ou à fournir
                montant=detail.quantite * 0,  # À calculer
                station_id=detail.station_id
            )
            db.add(ligne)

        # Créer les paiements
        for reglement in achat_data.reglements:
            # Valider que la trésorerie a suffisamment de fonds pour le paiement
            valider_paiement_achat_carburant(
                db,
                reglement.tresorerie_station_id,
                reglement.montant
            )

            paiement = PaiementAchatCarburant(
                achat_carburant_id=achat.id,
                date_paiement=reglement.date,
                montant=reglement.montant,
                mode_paiement=reglement.mode_paiement,
                tresorerie_station_id=reglement.tresorerie_station_id
            )
            db.add(paiement)

            # Récupérer un journal d'opérations existant
            from ...models.journal_operations import JournalOperations
            journal_ops = db.query(JournalOperations).first()
            if not journal_ops:
                # Si aucun journal n'existe, créer un journal par défaut
                journal_ops = JournalOperations(
                    nom="Journal des opérations",
                    code="JO001",  # Code unique
                    description="Journal principal des opérations",
                    type_journal="general",  # Type de journal
                    utilisateur_id=utilisateur_id  # ID de l'utilisateur connecté
                )
                db.add(journal_ops)
                db.flush()  # Pour obtenir l'ID

            # Créer les écritures comptables pour chaque paiement
            # Créer une écriture de trésorerie (débit) - entrée de fonds
            tresorerie_debit = OperationJournal(
                journal_operations_id=journal_ops.id,  # Utiliser l'ID du journal existant
                date_operation=reglement.date,
                libelle_operation=f"Paiement pour l'achat carburant {achat.id}",
                compte_debit="512",  # Compte de trésorerie
                compte_credit="401",  # Compte fournisseur
                montant=float(reglement.montant),
                devise="XOF",
                reference_operation=f"PA{paiement.id}",
                module_origine="achats_carburant",
                utilisateur_enregistrement_id=utilisateur_id  # Ajouter l'utilisateur
            )
            db.add(tresorerie_debit)

        # db.commit() n'est pas nécessaire ici car la transaction est gérée par FastAPI
        db.flush()  # Pour s'assurer que tout est synchronisé avant de rafraîchir
        db.refresh(achat)

        # Mettre à jour le solde du fournisseur après la création de l'achat
        # Trouver la station_id à partir des détails de l'achat
        if achat_data.details:
            station_id = achat_data.details[0].station_id
            mettre_a_jour_solde_apres_achat(
                db=db,
                achat_id=achat.id,
                utilisateur_id=utilisateur_id
            )

        return achat

    except Exception as e:
        # Laisser FastAPI gérer le rollback
        raise e


def annuler_achat_carburant(
    db: Session,
    achat_id: UUID,
    utilisateur_id: UUID,
    motif: str = None
) -> bool:
    """
    Annuler un achat de carburant et gérer toutes les opérations associées.

    Args:
        db: Session de base de données
        achat_id: ID de l'achat à annuler
        utilisateur_id: ID de l'utilisateur effectuant l'annulation
        motif: Motif de l'annulation

    Returns:
        bool: True si l'annulation a réussi
    """
    try:
        with db.begin():
            # Récupérer l'achat
            achat = db.query(AchatCarburant).filter(AchatCarburant.id == achat_id).first()
            if not achat:
                raise ValueError(f"Achat carburant avec l'ID {achat_id} non trouvé")

            # Vérifier si l'achat est déjà annulé
            if achat.statut == "annulé":
                raise ValueError("L'achat est déjà annulé")

            # Vérifier si des livraisons sont déjà associées à cet achat
            from ...models.livraison import Livraison
            livraisons = db.query(Livraison).filter(Livraison.achat_carburant_id == achat_id).all()
            if livraisons:
                raise ValueError("Impossible d'annuler un achat qui a déjà fait l'objet d'une ou plusieurs livraisons.")

            # Récupérer les paiements associés pour les annuler
            paiements = db.query(PaiementAchatCarburant).filter(
                PaiementAchatCarburant.achat_carburant_id == achat_id
            ).all()

            # Annuler les paiements
            for paiement in paiements:
                # Créer des écritures comptables inverses
                operation_inverse = OperationJournal(
                    journal_operations_id=uuid.uuid4(),
                    date_operation=datetime.now(),
                    libelle_operation=f"Annulation du paiement pour l'achat carburant {achat_id} (Motif: {motif or 'N/A'})",
                    compte_debit="401",  # Compte fournisseur (inverse de l'original)
                    compte_credit="512",  # Compte de trésorerie (inverse de l'original)
                    montant=float(paiement.montant),
                    devise="XOF",
                    reference_operation=f"AN{paiement.id}",
                    module_origine="achats_carburant"
                )
                db.add(operation_inverse)

                # Mettre à jour le statut du paiement
                paiement.statut = "annulé"

            # Mettre à jour le statut de l'achat
            achat.statut = "annulé"

            # Ajouter le motif d'annulation aux autres_infos s'il existe
            if motif:
                if achat.autres_infos:
                    achat.autres_infos["motif_annulation"] = motif
                else:
                    achat.autres_infos = {"motif_annulation": motif}

            db.commit()

            # Mettre à jour le solde du fournisseur après l'annulation
            # Trouver la station_id à partir des lignes d'achat
            ligne_achat = db.query(LigneAchatCarburant).filter(
                LigneAchatCarburant.achat_carburant_id == achat_id
            ).first()

            if ligne_achat:
                mettre_a_jour_solde_fournisseur(
                    db=db,
                    tiers_id=achat.fournisseur_id,
                    station_id=ligne_achat.station_id,
                    utilisateur_id=utilisateur_id
                )

            return True

    except Exception as e:
        db.rollback()
        raise e


def modifier_achat_carburant_complet(
    db: Session,
    achat_id: UUID,
    achat_data: AchatCarburantCreateWithDetails,
    utilisateur_id: UUID
) -> AchatCarburant:
    """
    Modifier un achat de carburant existant avec de nouveaux détails et paiements.

    Args:
        db: Session de base de données
        achat_id: ID de l'achat à modifier
        achat_data: Nouvelles données de l'achat avec détails et paiements
        utilisateur_id: ID de l'utilisateur effectuant l'opération

    Returns:
        AchatCarburant: L'achat modifié avec ses relations
    """
    try:
        with db.begin():
            # Récupérer l'achat existant
            achat = db.query(AchatCarburant).filter(AchatCarburant.id == achat_id).first()
            if not achat:
                raise ValueError(f"Achat carburant avec l'ID {achat_id} non trouvé")

            # Vérifier que l'achat est en statut "brouillon" pour permettre la modification
            if achat.statut != "brouillon":
                raise ValueError(f"Impossible de modifier un achat avec le statut '{achat.statut}'. Seuls les achats en statut 'brouillon' peuvent être modifiés.")

            # Vérifier si des livraisons sont déjà associées à cet achat
            from ...models.livraison import Livraison
            livraisons = db.query(Livraison).filter(Livraison.achat_carburant_id == achat_id).all()
            if livraisons:
                raise ValueError("Impossible de modifier un achat qui a déjà fait l'objet d'une ou plusieurs livraisons.")

            # Vérifier que le fournisseur existe
            from ...models.tiers import Tiers
            fournisseur = db.query(Tiers).filter(
                Tiers.id == achat_data.fournisseur_id,
                Tiers.type == 'fournisseur'
            ).first()

            if not fournisseur:
                raise ValueError(f"Fournisseur avec l'ID {achat_data.fournisseur_id} non trouvé")

            # Récupérer la compagnie de l'utilisateur connecté
            from ...models.user import User
            utilisateur = db.query(User).filter(User.id == utilisateur_id).first()
            if not utilisateur:
                raise ValueError(f"Utilisateur avec l'ID {utilisateur_id} non trouvé")

            # Mettre à jour les informations de base de l'achat
            achat.fournisseur_id = achat_data.fournisseur_id
            achat.date_achat = achat_data.date_achat
            achat.autres_infos = {"numero_bl": achat_data.numero_bl} if achat_data.numero_bl else None
            achat.numero_facture = achat_data.numero_facture
            achat.montant_total = achat_data.montant_total
            achat.compagnie_id = utilisateur.compagnie_id  # Récupérer automatiquement la compagnie de l'utilisateur

            # Supprimer les anciennes lignes d'achat
            lignes_anciennes = db.query(LigneAchatCarburant).filter(
                LigneAchatCarburant.achat_carburant_id == achat_id
            ).all()

            for ligne in lignes_anciennes:
                db.delete(ligne)

            # Créer les nouvelles lignes d'achat
            for detail in achat_data.details:
                ligne = LigneAchatCarburant(
                    achat_carburant_id=achat.id,
                    carburant_id=detail.carburant_id,
                    quantite=detail.quantite,
                    prix_unitaire=0,  # À calculer ou à fournir
                    montant=detail.quantite * 0,  # À calculer
                    station_id=detail.station_id
                )
                db.add(ligne)

            # Supprimer les anciens paiements (ne pas supprimer si déjà validés ou utilisés)
            paiements_anciens = db.query(PaiementAchatCarburant).filter(
                PaiementAchatCarburant.achat_carburant_id == achat_id
            ).all()

            for paiement in paiements_anciens:
                # Si le paiement est déjà validé, il pourrait être nécessaire de créer une opération d'annulation
                # plutot que de supprimer directement
                if paiement.statut == "validé":
                    # Créer une opération d'annulation
                    operation_inverse = OperationJournal(
                        journal_operations_id=uuid.uuid4(),
                        date_operation=datetime.now(),
                        libelle_operation=f"Annulation du paiement pour modification de l'achat carburant {achat_id}",
                        compte_debit="401",  # Compte fournisseur (inverse de l'original)
                        compte_credit="512",  # Compte de trésorerie (inverse de l'original)
                        montant=float(paiement.montant),
                        devise="XOF",
                        reference_operation=f"AN{paiement.id}",
                        module_origine="achats_carburant"
                    )
                    db.add(operation_inverse)

                # Mise à jour du statut du paiement existant
                paiement.statut = "annulé"

            # Créer les nouveaux paiements
            for reglement in achat_data.reglements:
                # Valider que la trésorerie a suffisamment de fonds pour le paiement
                valider_paiement_achat_carburant(
                    db,
                    reglement.tresorerie_station_id,
                    reglement.montant
                )

                paiement = PaiementAchatCarburant(
                    achat_carburant_id=achat.id,
                    date_paiement=reglement.date,
                    montant=reglement.montant,
                    mode_paiement=reglement.mode_paiement,
                    tresorerie_station_id=reglement.tresorerie_station_id
                )
                db.add(paiement)

                # Créer les écritures comptables pour chaque nouveau paiement
                tresorerie_debit = OperationJournal(
                    journal_operations_id=uuid.uuid4(),
                    date_operation=reglement.date,
                    libelle_operation=f"Paiement pour l'achat carburant {achat.id}",
                    compte_debit="512",  # Compte de trésorerie
                    compte_credit="401",  # Compte fournisseur
                    montant=float(reglement.montant),
                    devise="XOF",
                    reference_operation=f"PA{paiement.id}",
                    module_origine="achats_carburant"
                )
                db.add(tresorerie_debit)

            db.commit()
            db.refresh(achat)

            # Mettre à jour le solde du fournisseur après la modification
            if achat_data.details:
                station_id = achat_data.details[0].station_id
                mettre_a_jour_solde_fournisseur(
                    db=db,
                    tiers_id=achat.fournisseur_id,
                    station_id=station_id,
                    utilisateur_id=utilisateur_id
                )

            return achat

    except Exception as e:
        db.rollback()
        raise e