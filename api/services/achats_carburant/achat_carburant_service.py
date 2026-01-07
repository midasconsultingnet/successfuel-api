from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from sqlalchemy import func
from ...models.achat_carburant import AchatCarburant, LigneAchatCarburant, PaiementAchatCarburant
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
from ..tresorerie.mouvement_manager import MouvementTresorerieManager
from ...services.comptabilite import ComptabiliteManager, TypeOperationComptable
import uuid
from datetime import datetime, timezone


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

        # Récupérer la compagnie de l'utilisateur (soit de l'achat_data si fournie, soit de l'utilisateur)
        compagnie_id = achat_data.compagnie_id if achat_data.compagnie_id else utilisateur.compagnie_id

        # Créer l'achat principal
        achat = AchatCarburant(
            fournisseur_id=achat_data.fournisseur_id,
            date_achat=achat_data.date_achat,
            autres_infos={"numero_bl": achat_data.numero_bl} if achat_data.numero_bl else None,
            numero_facture=achat_data.numero_facture,
            montant_total=achat_data.montant_total,
            compagnie_id=compagnie_id,  # Récupérer automatiquement la compagnie de l'utilisateur ou utiliser celle fournie
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

        # Calculer la dette fournisseur (montant total - paiements effectués)
        total_paiements = sum(reglement.montant for reglement in achat_data.reglements)
        dette_fournisseur = achat_data.montant_total - total_paiements

        # Créer les paiements
        for reglement in achat_data.reglements:
            # Récupérer l'utilisateur pour la validation
            from ...models.user import User
            utilisateur = db.query(User).filter(User.id == utilisateur_id).first()

            # Valider que la trésorerie a suffisamment de fonds pour le paiement
            valider_paiement_achat_carburant(
                db,
                reglement.tresorerie_id,  # Utiliser le champ existant
                reglement.montant,
                utilisateur=utilisateur
            )

            paiement = PaiementAchatCarburant(
                achat_carburant_id=achat.id,
                date_paiement=reglement.date,
                montant=reglement.montant,
                mode_paiement=reglement.mode_paiement,
                tresorerie_station_id=reglement.tresorerie_id  # Utiliser le champ existant
            )
            db.add(paiement)

            # Créer un mouvement de trésorerie pour enregistrer la sortie d'argent via le gestionnaire
            try:
                mouvement = MouvementTresorerieManager.creer_mouvement_paiement_achat_carburant(
                    db=db,
                    paiement_achat_id=paiement.id,
                    utilisateur_id=utilisateur_id
                )
            except Exception as e:
                # If treasury movement creation fails, we should handle it appropriately
                # For now, we'll just log the error, but in a real application you might want to rollback
                print(f"Error creating treasury movement for paiement achat carburant {paiement.id}: {str(e)}")

        # Enregistrer l'écriture comptable pour l'achat
        try:
            # Enregistrer l'achat en tant que dette (ou partie payée)
            # Si des paiements ont été faits, enregistrer les écritures de trésorerie
            for reglement in achat_data.reglements:
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=TypeOperationComptable.ACHAT_CARBURANT,
                    reference_origine=f"PAC-{paiement.id}",
                    montant=reglement.montant,
                    compte_debit="607",  # Achats de carburant
                    compte_credit="512",  # Trésorerie
                    libelle=f"Paiement pour achat carburant #{achat.id}",
                    utilisateur_id=utilisateur_id
                )

            # Si il y a une dette restante, enregistrer l'écriture de dette fournisseur
            if dette_fournisseur > 0:
                ComptabiliteManager.enregistrer_ecriture_double(
                    db=db,
                    type_operation=TypeOperationComptable.ACHAT_CARBURANT,
                    reference_origine=f"DETTE-{achat.id}",
                    montant=dette_fournisseur,
                    compte_debit="401",  # Fournisseurs
                    compte_credit="607",  # Achats de carburant
                    libelle=f"Dette fournisseur pour achat carburant #{achat.id}",
                    utilisateur_id=utilisateur_id
                )
        except Exception as e:
            # En cas d'erreur, on continue sans l'écriture comptable
            print(f"Erreur lors de l'enregistrement de l'écriture comptable pour l'achat {achat.id}: {str(e)}")

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
                # Mettre à jour le statut du paiement
                paiement.statut = "annulé"

            # Annuler les mouvements de trésorerie associés à l'achat via le gestionnaire
            # Note: We need to find the actual treasury movements linked to these payments
            try:
                # Trouver les mouvements de trésorerie liés aux paiements de cet achat
                from ...models.tresorerie import MouvementTresorerie
                for paiement in paiements:
                    mouvements = db.query(MouvementTresorerie).filter(
                        MouvementTresorerie.reference_origine.like(f"PAC-{paiement.id}%")
                    ).all()

                    for mouvement in mouvements:
                        mouvement_annulation = MouvementTresorerieManager.annuler_mouvement(
                            db=db,
                            mouvement_id=mouvement.id,
                            utilisateur_id=utilisateur_id,
                            motif=motif or "Annulation d'achat"
                        )
            except Exception as e:
                # If treasury movement cancellation fails, we should handle it appropriately
                # For now, we'll just log the error, but in a real application you might want to rollback
                print(f"Error cancelling treasury movement for achat carburant {achat_id}: {str(e)}")

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


def traiter_livraison_achat_carburant(
    db: Session,
    achat_id: UUID,
    utilisateur_id: UUID
) -> AchatCarburant:
    """
    Traiter la livraison d'un achat de carburant, met à jour les stocks et les soldes fournisseurs.
    Cela correspond à l'étape 3 du processus : enregistrement de la livraison avec récapitulation automatique.

    Args:
        db: Session de base de données
        achat_id: ID de l'achat à traiter pour la livraison
        utilisateur_id: ID de l'utilisateur effectuant l'opération

    Returns:
        AchatCarburant: L'achat mis à jour avec les informations de livraison
    """
    try:
        with db.begin():
            # Récupérer l'achat
            achat = db.query(AchatCarburant).filter(AchatCarburant.id == achat_id).first()
            if not achat:
                raise ValueError(f"Achat carburant avec l'ID {achat_id} non trouvé")

            # Vérifier que l'achat est en statut "validé" pour permettre le traitement de la livraison
            if achat.statut != "validé":
                raise ValueError(f"Impossible de traiter la livraison d'un achat avec le statut '{achat.statut}'. Seuls les achats validés peuvent être livrés.")

            # Obtenir les livraisons associées à cet achat
            from ...models.livraison import Livraison
            livraisons = db.query(Livraison).filter(
                Livraison.achat_carburant_id == achat_id
            ).all()

            if not livraisons:
                raise ValueError("Aucune livraison associée à cet achat")

            # Calculer les quantités réelles des livraisons
            quantite_totale_livree = sum(float(l.quantite_livree) for l in livraisons)

            # Calculer les quantités théoriques de l'achat
            lignes_achat = db.query(LigneAchatCarburant).filter(
                LigneAchatCarburant.achat_carburant_id == achat_id
            ).all()
            quantite_totale_commandee = sum(float(l.quantite) for l in lignes_achat)

            # Calculer le montant réel basé sur la livraison
            # Cela suppose que tous les articles de l'achat ont le même prix unitaire
            # En pratique, vous devrez peut-être calculer une moyenne pondérée
            if quantite_totale_commandee > 0:
                prix_unitaire_moyen = float(achat.montant_total) / quantite_totale_commandee
                montant_reel = quantite_totale_livree * prix_unitaire_moyen
            else:
                montant_reel = 0

            # Mettre à jour l'achat avec les informations de livraison
            achat.montant_reel = montant_reel
            achat.ecart_achat_livraison = float(achat.montant_total) - montant_reel
            achat.statut = "livré"  # Devient "facturé" dans l'ancienne terminologie
            achat.date_livraison = datetime.now(timezone.utc)

            # Créer les mouvements de stock pour chaque livraison
            from ...models.compagnie import MouvementStockCuve
            for livraison in livraisons:
                # Créer l'enregistrement de mouvement de stock
                mouvement_stock = MouvementStockCuve(
                    livraison_carburant_id=livraison.id,
                    cuve_id=livraison.cuve_id,
                    type_mouvement="entrée",  # La livraison augmente le stock
                    quantite=livraison.quantite_livree,
                    date_mouvement=livraison.date_livraison,
                    utilisateur_id=utilisateur_id,
                    reference_origine=f"LIV-{str(livraison.id)[:8]}",
                    module_origine="livraisons",
                    statut="validé"
                )
                db.add(mouvement_stock)

            # Ajuster le solde fournisseur en fonction de la différence entre le payé et le livré
            ecart_paiement_livraison = float(achat.montant_total) - montant_reel

            # Obtenir le total des paiements effectués pour cet achat
            paiements = db.query(PaiementAchatCarburant).filter(
                PaiementAchatCarburant.achat_carburant_id == achat_id
            ).all()
            total_paiements = sum(p.montant for p in paiements)

            # Calculer l'ajustement nécessaire
            ajustement_solde = float(total_paiements) - montant_reel

            if ajustement_solde != 0:
                mettre_a_jour_solde_fournisseur(
                    db=db,
                    tiers_id=achat.fournisseur_id,
                    station_id=achat.ligne_achat_carburant[0].station_id if achat.ligne_achat_carburant else None,
                    utilisateur_id=utilisateur_id
                )

            db.commit()
            db.refresh(achat)

            return achat

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

            # Récupérer la compagnie de l'utilisateur (soit de l'achat_data si fournie, soit de l'utilisateur)
            compagnie_id = achat_data.compagnie_id if achat_data.compagnie_id else utilisateur.compagnie_id

            # Mettre à jour les informations de base de l'achat
            achat.fournisseur_id = achat_data.fournisseur_id
            achat.date_achat = achat_data.date_achat
            achat.autres_infos = {"numero_bl": achat_data.numero_bl} if achat_data.numero_bl else None
            achat.numero_facture = achat_data.numero_facture
            achat.montant_total = achat_data.montant_total
            achat.compagnie_id = compagnie_id  # Récupérer automatiquement la compagnie de l'utilisateur ou utiliser celle fournie

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

            # Calculer la dette fournisseur (montant total - paiements effectués)
            total_paiements = sum(reglement.montant for reglement in achat_data.reglements)
            dette_fournisseur = achat_data.montant_total - total_paiements

            # Supprimer les anciens paiements (ne pas supprimer si déjà validés ou utilisés)
            paiements_anciens = db.query(PaiementAchatCarburant).filter(
                PaiementAchatCarburant.achat_carburant_id == achat_id
            ).all()

            for paiement in paiements_anciens:
                # Mise à jour du statut du paiement existant
                paiement.statut = "annulé"

            # Créer les nouveaux paiements
            for reglement in achat_data.reglements:
                # Récupérer l'utilisateur pour la validation
                from ...models.user import User
                utilisateur = db.query(User).filter(User.id == utilisateur_id).first()

                # Valider que la trésorerie a suffisamment de fonds pour le paiement
                valider_paiement_achat_carburant(
                    db,
                    reglement.tresorerie_id,  # Utiliser le champ existant
                    reglement.montant,
                    utilisateur=utilisateur
                )

                paiement = PaiementAchatCarburant(
                    achat_carburant_id=achat.id,
                    date_paiement=reglement.date,
                    montant=reglement.montant,
                    mode_paiement=reglement.mode_paiement,
                    tresorerie_station_id=reglement.tresorerie_id  # Utiliser le champ existant
                )
                db.add(paiement)

                # Créer un mouvement de trésorerie pour enregistrer la sortie d'argent via le gestionnaire
                try:
                    mouvement = MouvementTresorerieManager.creer_mouvement_paiement_achat_carburant(
                        db=db,
                        paiement_achat_id=paiement.id,
                        utilisateur_id=utilisateur_id
                    )
                except Exception as e:
                    # If treasury movement creation fails, we should handle it appropriately
                    # For now, we'll just log the error, but in a real application you might want to rollback
                    print(f"Error creating treasury movement for paiement achat carburant {paiement.id}: {str(e)}")

            # Enregistrer l'écriture comptable pour l'achat
            try:
                # Supprimer les anciennes écritures comptables pour cet achat
                from ...models.operation_journal import OperationJournal
                anciennes_ecritures = db.query(OperationJournal).filter(
                    OperationJournal.reference_operation.like(f"AC-{achat_id}%")
                ).all()
                for ecriture in anciennes_ecritures:
                    db.delete(ecriture)

                # Enregistrer les nouvelles écritures comptables
                for reglement in achat_data.reglements:
                    ComptabiliteManager.enregistrer_ecriture_double(
                        db=db,
                        type_operation=TypeOperationComptable.ACHAT_CARBURANT,
                        reference_origine=f"PAC-{paiement.id}",
                        montant=reglement.montant,
                        compte_debit="607",  # Achats de carburant
                        compte_credit="512",  # Trésorerie
                        libelle=f"Paiement pour achat carburant #{achat.id}",
                        utilisateur_id=utilisateur_id
                    )

                # Si il y a une dette restante, enregistrer l'écriture de dette fournisseur
                if dette_fournisseur > 0:
                    ComptabiliteManager.enregistrer_ecriture_double(
                        db=db,
                        type_operation=TypeOperationComptable.ACHAT_CARBURANT,
                        reference_origine=f"DETTE-{achat.id}",
                        montant=dette_fournisseur,
                        compte_debit="401",  # Fournisseurs
                        compte_credit="607",  # Achats de carburant
                        libelle=f"Dette fournisseur pour achat carburant #{achat.id}",
                        utilisateur_id=utilisateur_id
                    )
            except Exception as e:
                # En cas d'erreur, on continue sans l'écriture comptable
                print(f"Erreur lors de l'enregistrement de l'écriture comptable pour l'achat {achat.id}: {str(e)}")

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