from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ClassificationEcart(str, Enum):
    PERTE = "perte"
    EVAPORATION = "evaporation"
    ANOMALIE = "anomalie"
    SURPLUS = "surplus"

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

class EcartInventaireBase(BaseModel):
    inventaire_id: str
    produit_id: str
    station_id: str
    compagnie_id: str
    quantite_theorique: float
    quantite_reelle: float
    ecart: float
    classification: ClassificationEcart
    seuil_alerte: Optional[float] = None
    seuil_saison: Optional[str] = None
    motif_anomalie: Optional[str] = None

class EcartInventaireCreate(EcartInventaireBase):
    pass

class EcartInventaireUpdate(BaseModel):
    quantite_theorique: Optional[float] = None
    quantite_reelle: Optional[float] = None
    ecart: Optional[float] = None
    classification: Optional[ClassificationEcart] = None
    seuil_alerte: Optional[float] = None
    seuil_saison: Optional[str] = None
    motif_anomalie: Optional[str] = None

class EcartInventaireResponse(EcartInventaireBase):
    id: str
    date_creation: datetime
    date_modification: datetime
    est_actif: bool

    class Config:
        from_attributes = True