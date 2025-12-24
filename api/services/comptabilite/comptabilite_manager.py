from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional
from ...models.journal_comptable import JournalComptable
from ...models.operation_journal import OperationJournal
from ...models.journal_operations import JournalOperations
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
        compte_debit: str,
        compte_credit: str,
        libelle: str,
        utilisateur_id: UUID,
        date_operation: Optional[datetime] = None,
        devise: str = "XOF"
    ) -> OperationJournal:
        """
        Enregistre une écriture comptable dans le journal
        """
        if date_operation is None:
            date_operation = datetime.utcnow()
        
        # Récupérer ou créer le journal des opérations par défaut
        journal_operations_id = ComptabiliteManager._get_default_journal_id(db, utilisateur_id)
        
        # Créer un enregistrement dans le journal des opérations
        operation_journal = OperationJournal(
            journal_operations_id=journal_operations_id,
            date_operation=date_operation,
            libelle_operation=libelle,
            compte_debit=compte_debit,
            compte_credit=compte_credit,
            montant=montant,
            devise=devise,
            reference_operation=reference_origine,
            module_origine=type_operation.value,
            utilisateur_enregistrement_id=utilisateur_id
        )
        
        db.add(operation_journal)
        db.commit()
        db.refresh(operation_journal)
        
        return operation_journal
    
    @staticmethod
    def enregistrer_ecriture_double(
        db: Session,
        type_operation: TypeOperationComptable,
        reference_origine: str,
        montant: float,
        compte_debit: str,
        compte_credit: str,
        libelle: str,
        utilisateur_id: UUID,
        date_operation: Optional[datetime] = None,
        devise: str = "XOF"
    ) -> tuple[OperationJournal, OperationJournal]:
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
            devise=devise
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
            devise=devise
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