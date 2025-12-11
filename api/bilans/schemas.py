from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BilanOperationnel(BaseModel):
    date_debut: datetime
    date_fin: datetime
    total_ventes: float
    total_achats: float
    resultat: float
    details: Optional[dict] = None  # Additional details in JSON format

class BilanTresorerie(BaseModel):
    date_debut: datetime
    date_fin: datetime
    solde_initial: float
    solde_final: float
    total_entrees: float
    total_sorties: float
    details: Optional[dict] = None  # Additional details in JSON format

class BilanStocks(BaseModel):
    date: datetime
    details: dict  # Details in JSON format
    # Example: {
    #   "carburant": {"essence": 10000, "diesel": 8000},
    #   "boutique": {"total_value": 500000},
    #   "gaz": {"total_value": 200000}
    # }

class BilanTiers(BaseModel):
    date: datetime
    type_tiers: str  # client, fournisseur, employe
    details: dict  # Details in JSON format