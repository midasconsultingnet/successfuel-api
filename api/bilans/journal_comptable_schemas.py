from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class EcritureComptable(BaseModel):
    """Modèle pour une écriture comptable"""
    id: uuid.UUID
    date_ecriture: datetime
    libelle: str
    compte_debit: str  # Numéro du compte de débit
    compte_credit: str  # Numéro du compte de crédit
    montant: float
    devise: str = "XOF"
    reference: str  # Référence de l'opération d'origine
    module_origine: str  # Le module qui a généré l'opération
    details: Optional[dict] = None


class JournalComptableResponse(BaseModel):
    """Modèle de réponse pour le journal comptable"""
    date_debut: datetime
    date_fin: datetime
    items: List[EcritureComptable]
    total_items: int
    total_debit: float
    total_credit: float