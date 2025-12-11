from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AchatCarburantCreate(BaseModel):
    fournisseur_id: str  # UUID
    date_achat: datetime
    numero_bl: str
    numero_facture: str
    montant_total: float
    station_id: str  # UUID
    utilisateur_id: str  # UUID

class AchatCarburantUpdate(BaseModel):
    numero_bl: Optional[str] = None
    numero_facture: Optional[str] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None  # brouillon, validé, facturé, annulé
    utilisateur_id: Optional[str] = None

class LigneAchatCarburantCreate(BaseModel):
    achat_carburant_id: str  # UUID
    carburant_id: str  # UUID
    quantite: float
    prix_unitaire: float
    montant: float
    cuve_id: str  # UUID

class LigneAchatCarburantUpdate(BaseModel):
    quantite: Optional[float] = None
    prix_unitaire: Optional[float] = None
    montant: Optional[float] = None

class CompensationFinanciereCreate(BaseModel):
    achat_carburant_id: str  # UUID
    type_compensation: str  # "avoir_reçu", "avoir_dû"
    quantite_theorique: float
    quantite_reelle: float
    difference: float
    montant_compensation: float
    motif: Optional[str] = None

class CompensationFinanciereUpdate(BaseModel):
    statut: Optional[str] = None  # émis, utilisé, partiellement_utilisé, expiré
    motif: Optional[str] = None

class AvoirCompensationCreate(BaseModel):
    compensation_financiere_id: str  # UUID
    tiers_id: str  # UUID
    montant: float
    motif: str
    utilisateur_emission_id: str  # UUID