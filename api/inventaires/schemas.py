from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InventaireCreate(BaseModel):
    produit_id: Optional[str] = None  # For boutique inventory
    cuve_id: Optional[str] = None  # For fuel tank inventory
    quantite_reelle: int  # Physical count
    date: datetime
    statut: str  # brouillon, en_cours, termine, valide, rapproche, cloture
    utilisateur_id: str  # UUID of the user who performed the count
    commentaires: Optional[str] = None
    seuil_tolerance: Optional[float] = 0  # Tolerance threshold for alerts
    methode_mesure: Optional[str] = "manuel"  # manuel, jauge_digitale, sonde_automatique (for fuel)

class InventaireUpdate(BaseModel):
    quantite_reelle: Optional[int] = None
    statut: Optional[str] = None
    commentaires: Optional[str] = None
    utilisateur_id: Optional[str] = None