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
    montant_initial: float
    montant_utilise: Optional[float] = 0
    montant_restant: Optional[float] = None
    date_emission: datetime
    date_utilisation: Optional[datetime] = None
    date_expiration: Optional[datetime] = None
    motif: str
    statut: Optional[str] = "emis"  # émis, utilisé, partiellement_utilisé, expiré
    utilisateur_emission_id: str  # UUID of the user who created the credit note
    utilisateur_utilisation_id: Optional[str] = None  # UUID of the user who used the credit note
    reference_origine: str  # Référence d'origine de l'avoir
    module_origine: str  # Module d'origine : ventes, achats, compensations
    numero_piece_comptable: Optional[str] = None

class AvoirUpdate(BaseModel):
    montant_initial: Optional[float] = None
    montant_utilise: Optional[float] = None
    montant_restant: Optional[float] = None
    date_utilisation: Optional[datetime] = None
    date_expiration: Optional[datetime] = None
    statut: Optional[str] = None  # émis, utilisé, partiellement_utilisé, expiré
    utilisateur_utilisation_id: Optional[str] = None  # UUID of the user who used the credit note
    reference_origine: Optional[str] = None  # Référence d'origine de l'avoir
    module_origine: Optional[str] = None  # Module d'origine : ventes, achats, compensations
    numero_piece_comptable: Optional[str] = None