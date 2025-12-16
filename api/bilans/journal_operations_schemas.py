from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class JournalOperationItem(BaseModel):
    """Modèle pour un élément du journal des opérations"""
    id: uuid.UUID
    type_operation: str  # vente, achat, charge, salaire, mouvement_trésorerie, etc.
    date_operation: datetime
    montant: float
    devise: str = "XOF"
    description: str
    station_id: uuid.UUID
    reference: str  # Référence de l'opération dans le module d'origine
    module_origine: str  # Le module qui a généré l'opération
    details: Optional[dict] = None


class JournalOperationsResponse(BaseModel):
    """Modèle de réponse pour le journal des opérations"""
    date_debut: datetime
    date_fin: datetime
    station_id: Optional[uuid.UUID] = None
    type_operation: Optional[str] = None
    items: List[JournalOperationItem]
    total_items: int
    total_montant: float