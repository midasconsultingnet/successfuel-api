from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TresorerieCreate(BaseModel):
    nom: str
    type: str  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde: Optional[float] = 0
    informations_bancaires: Optional[str] = None  # JSON string for bank details
    compagnie_id: str  # UUID of the company
    station_id: str  # UUID of the station this treasury belongs to

class TresorerieUpdate(BaseModel):
    nom: Optional[str] = None
    type: Optional[str] = None
    solde: Optional[float] = None
    statut: Optional[bool] = None
    informations_bancaires: Optional[str] = None

class TransfertCreate(BaseModel):
    tresorerie_source_id: str  # UUID
    tresorerie_destination_id: str  # UUID
    montant: float
    date: datetime
    description: Optional[str] = None
    utilisateur_id: str  # UUID of the user who made the transfer
    numero_piece_comptable: Optional[str] = None
    compagnie_id: str  # UUID of the company

class TransfertUpdate(BaseModel):
    description: Optional[str] = None
    numero_piece_comptable: Optional[str] = None