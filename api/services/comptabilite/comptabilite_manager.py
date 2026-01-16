from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional
from ...models.journal_comptable import JournalComptable
from ...models.journal_operations import JournalOperations
from ...models.ecriture_comptable import EcritureComptableModel
from ...models.user import User
from ...exceptions import InvalidTransactionException


class TypeOperationComptable(str, Enum):
    ACHAT_CARBURANT = "achats_carburant"
    VENTE_CARBURANT = "ventes_carburant"
    ACHAT_BOUTIQUE = "achats_boutique"
    VENTE_BOUTIQUE = "ventes_boutique"
    MOUVEMENT_TRESORERIE = "mouvement_tresorerie"
    TRANSFERT_TRESORERIE = "transfert_tresorerie"
    CHARGE = "charges"
    SALAIRE = "salaires"
    TIERS_SOLDE_INITIAL = "tiers_solde_initial"


class ComptabiliteManager:
    """
    Classe centralisée pour la gestion des écritures comptables.
    """
    
    @staticmethod
    def enregistrer_ecriture_comptable(
        db: Session,
        type_operation: TypeOperationComptable,
        reference_origine: str,
        montant: float,
        compte_debit: UUID,
        compte_credit: UUID,
        libelle: str,
        utilisateur_id: UUID,
        date_operation: Optional[datetime] = None,
        devise: str = "XOF",
        compagnie_id: Optional[UUID] = None,
        tiers_id: Optional[UUID] = None
    ) -> EcritureComptableModel:
        """
        Enregistre une écriture comptable dans la table ecriture_comptable
        """
        if date_operation is None:
            date_operation = datetime.utcnow()

        # Récupérer la compagnie de l'utilisateur si non fournie
        if not compagnie_id:
            utilisateur = db.query(User).filter(User.id == utilisateur_id).first()
            if utilisateur:
                compagnie_id = utilisateur.compagnie_id

        # Créer un enregistrement dans la table ecriture_comptable
        ecriture_comptable = EcritureComptableModel(
            date_ecriture=date_operation,
            libelle_ecriture=libelle,
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            montant=montant,
            devise=devise,
            tiers_id=tiers_id,
            module_origine=type_operation.value,
            reference_origine=reference_origine,
            utilisateur_id=utilisateur_id,
            compagnie_id=compagnie_id,
            est_validee=True,  # Par défaut, les nouvelles écritures sont validées
            est_actif=True
        )

        db.add(ecriture_comptable)
        db.commit()
        db.refresh(ecriture_comptable)

        return ecriture_comptable
    
    @staticmethod
    def enregistrer_ecriture_double(
        db: Session,
        type_operation: TypeOperationComptable,
        reference_origine: str,
        montant: float,
        compte_debit: UUID,
        compte_credit: UUID,
        libelle: str,
        utilisateur_id: UUID,
        date_operation: Optional[datetime] = None,
        devise: str = "XOF",
        compagnie_id: Optional[UUID] = None,
        tiers_id: Optional[UUID] = None
    ) -> tuple[EcritureComptableModel, EcritureComptableModel]:
        """
        Enregistre une écriture comptable double (débit et crédit)
        """
        if date_operation is None:
            date_operation = datetime.utcnow()

        # Créer l'écriture de débit
        debit_operation = ComptabiliteManager.enregistrer_ecriture_comptable(
            db=db,
            type_operation=type_operation,
            reference_origine=reference_origine,
            montant=montant,
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            libelle=f"{libelle} - Débit",
            utilisateur_id=utilisateur_id,
            date_operation=date_operation,
            devise=devise,
            compagnie_id=compagnie_id,
            tiers_id=tiers_id
        )

        # Créer l'écriture de crédit (inversée)
        credit_operation = ComptabiliteManager.enregistrer_ecriture_comptable(
            db=db,
            type_operation=type_operation,
            reference_origine=reference_origine,
            montant=montant,
            compte_debit=compte_credit,  # inversé
            compte_credit=compte_debit,  # inversé
            libelle=f"{libelle} - Crédit",
            utilisateur_id=utilisateur_id,
            date_operation=date_operation,
            devise=devise,
            compagnie_id=compagnie_id,
            tiers_id=tiers_id
        )

        return debit_operation, credit_operation
    
    @staticmethod
    def _get_default_journal_id(db: Session, utilisateur_id: UUID) -> UUID:
        """
        Récupère ou crée un journal des opérations par défaut
        """
        journal = db.query(JournalOperations).first()
        if not journal:
            journal = JournalOperations(
                nom="Journal des opérations principal",
                code="JO001",
                description="Journal principal des opérations comptables",
                type_journal="general",
                devise="XOF",
                utilisateur_id=utilisateur_id
            )
            db.add(journal)
            db.commit()
            db.refresh(journal)
        
        return journal.id