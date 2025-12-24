from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .journal_comptable_schemas import EcritureComptable, JournalComptableResponse
from fastapi import HTTPException


def get_journal_comptable(
    db: Session,
    date_debut: str,
    date_fin: str
) -> JournalComptableResponse:
    """
    Générer le journal comptable entre deux dates
    """
    from ..models.operation_journal import OperationJournal
    from ..models.journal_operations import JournalOperations

    try:
        date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide")

    items: List[EcritureComptable] = []
    total_debit = 0.0
    total_credit = 0.0

    # Récupérer les écritures comptables directement depuis OperationJournal
    operations = db.query(OperationJournal).filter(
        OperationJournal.date_operation >= date_debut_obj,
        OperationJournal.date_operation <= date_fin_obj
    ).all()

    for operation in operations:
        # Créer des écritures comptables à partir des opérations enregistrées
        debit_item = EcritureComptable(
            id=operation.id,
            date_ecriture=operation.date_operation,
            libelle=operation.libelle_operation,
            compte_debit=operation.compte_debit,
            compte_credit=operation.compte_credit,
            montant=float(operation.montant),
            devise=operation.devise,
            reference=operation.reference_operation,
            module_origine=operation.module_origine,
            details={}
        )
        items.append(debit_item)
        total_debit += float(operation.montant)

    # Trier par date d'écriture
    items.sort(key=lambda x: x.date_ecriture)

    response = JournalComptableResponse(
        date_debut=date_debut_obj,
        date_fin=date_fin_obj,
        items=items,
        total_items=len(items),
        total_debit=total_debit,
        total_credit=total_credit
    )

    # Vérifier que le total des débits égale le total des crédits (équilibre comptable)
    if abs(total_debit - total_credit) > 0.01:  # Tolérer une petite différence due aux arrondis
        print(f"ATTENTION: Le journal comptable n'est pas équilibré. Débit: {total_debit}, Crédit: {total_credit}")

    return response