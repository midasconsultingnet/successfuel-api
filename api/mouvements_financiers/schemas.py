from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReglementCreate(BaseModel):
    tiers_id: str  # UUID
    montant: float
    date: datetime
    methode_paiement: str  # cash, cheque, virement, mobile_money, note_credit
    numero_piece_comptable: Optional[str] = None
    date_echeance: Optional[datetime] = None
    utilisateur_id: str  # UUID of the user who recorded the payment

class ReglementUpdate(BaseModel):
    montant: Optional[float] = None
    date: Optional[datetime] = None
    methode_paiement: Optional[str] = None
    statut: Optional[str] = None  # en_attente, effectue, annule
    numero_piece_comptable: Optional[str] = None
    date_echeance: Optional[datetime] = None
    penalites: Optional[float] = None

class CreanceCreate(BaseModel):
    tiers_id: str  # UUID
    montant: float
    date: datetime
    date_echeance: Optional[datetime] = None
    motif: Optional[str] = None
    utilisateur_id: str  # UUID of the user who recorded the debt
    numero_piece_comptable: Optional[str] = None
    penalites: Optional[float] = 0

class CreanceUpdate(BaseModel):
    montant: Optional[float] = None
    date_echeance: Optional[datetime] = None
    statut: Optional[str] = None  # active, recouvre, echeance, douteuse
    motif: Optional[str] = None
    penalites: Optional[float] = None

class AvoirCreate(BaseModel):
    tiers_id: str  # UUID
    montant: float
    motif: str
    date: datetime
    date_expiration: Optional[datetime] = None
    utilisateur_id: str  # UUID of the user who created the credit note
    numero_piece_comptable: Optional[str] = None

class AvoirUpdate(BaseModel):
    montant: Optional[float] = None
    statut: Optional[str] = None  # emis, utilise, partiellement_utilise, expire
    date_expiration: Optional[datetime] = None