from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategorieChargeCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    type: str  # fixe, variable
    seuil_alerte: Optional[float] = None  # Threshold for budget alerts
    compte_comptable: Optional[str] = None  # Accounting account

class CategorieChargeUpdate(BaseModel):
    description: Optional[str] = None
    type: Optional[str] = None
    seuil_alerte: Optional[float] = None
    compte_comptable: Optional[str] = None

class ChargeCreate(BaseModel):
    categorie: str  # Name of the category
    fournisseur_id: Optional[str] = None  # Optional - service provider
    date: datetime
    montant: float
    description: Optional[str] = None
    date_echeance: Optional[datetime] = None
    methode_paiement: Optional[str] = None  # cash, cheque, virement, mobile_money
    numero_piece_comptable: Optional[str] = None
    utilisateur_id: str  # UUID of the user who recorded the expense

class ChargeUpdate(BaseModel):
    categorie: Optional[str] = None
    fournisseur_id: Optional[str] = None
    date: Optional[datetime] = None
    montant: Optional[float] = None
    description: Optional[str] = None
    date_echeance: Optional[datetime] = None
    statut: Optional[str] = None  # prevu, echu, paye, en_cours_paiement
    methode_paiement: Optional[str] = None
    numero_piece_comptable: Optional[str] = None
    solde_du: Optional[float] = None