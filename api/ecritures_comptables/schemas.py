from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class OperationJournalCreate(BaseModel):
    journal_operations_id: str  # UUID
    date_operation: datetime
    libelle_operation: str
    compte_debit: str
    compte_credit: str
    montant: float
    devise: Optional[str] = "XOF"
    reference_operation: str
    module_origine: str
    utilisateur_enregistrement_id: str  # UUID

class OperationJournalUpdate(BaseModel):
    libelle_operation: Optional[str] = None
    compte_debit: Optional[str] = None
    compte_credit: Optional[str] = None
    montant: Optional[float] = None
    reference_operation: Optional[str] = None
    utilisateur_enregistrement_id: Optional[str] = None