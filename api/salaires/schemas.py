from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SalaireCreate(BaseModel):
    employe_id: str  # UUID (Employee is a type of tier)
    periode: str  # Format: YYYY-MM
    date_echeance: datetime
    date_paiement: Optional[datetime] = None  # When was it paid
    salaire_base: float
    montant_total: float
    methode_paiement: Optional[str] = None  # cash, virement, cheque
    utilisateur_id: str  # UUID of the user who processed the payment
    numero_piece_comptable: Optional[str] = None

class SalaireUpdate(BaseModel):
    date_paiement: Optional[datetime] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None  # prevu, echu, paye, du
    methode_paiement: Optional[str] = None
    numero_piece_comptable: Optional[str] = None

class PrimeCreate(BaseModel):
    employe_id: str  # UUID
    montant: float
    motif: str
    date: datetime
    periode: Optional[str] = None  # Optional: to which period does this bonus apply
    utilisateur_id: str  # UUID of the user who created the bonus
    numero_piece_comptable: Optional[str] = None

class PrimeUpdate(BaseModel):
    montant: Optional[float] = None
    motif: Optional[str] = None
    periode: Optional[str] = None
    numero_piece_comptable: Optional[str] = None

class AvanceCreate(BaseModel):
    employe_id: str  # UUID
    montant: float
    date: datetime
    motif: Optional[str] = None
    date_echeance: Optional[datetime] = None  # When should it be repaid
    utilisateur_id: str  # UUID of the user who created the advance
    numero_piece_comptable: Optional[str] = None

class AvanceUpdate(BaseModel):
    date_echeance: Optional[datetime] = None
    montant_rembourse: Optional[float] = None
    statut: Optional[str] = None  # non_rembourse, en_cours, rembourse
    numero_piece_comptable: Optional[str] = None


class SalaireResponse(BaseModel):
    id: str = Field(
        ...,
        description="Identifiant unique du salaire",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    employe_id: str  # UUID (Employee is a type of tier)
    periode: str  # Format: YYYY-MM
    date_echeance: datetime
    date_paiement: Optional[datetime] = None  # When was it paid
    salaire_base: float
    montant_total: float
    methode_paiement: Optional[str] = None  # cash, virement, cheque
    utilisateur_id: str  # UUID of the user who processed the payment
    numero_piece_comptable: Optional[str] = None
    compagnie_id: str  # UUID de la compagnie associée
    date_creation: datetime
    date_modification: datetime
    est_actif: bool = True

    class Config:
        from_attributes = True


class PrimeResponse(BaseModel):
    id: str = Field(
        ...,
        description="Identifiant unique de la prime",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    employe_id: str  # UUID
    montant: float
    motif: str
    date: datetime
    periode: Optional[str] = None  # Optional: to which period does this bonus apply
    utilisateur_id: str  # UUID of the user who created the bonus
    numero_piece_comptable: Optional[str] = None
    compagnie_id: str  # UUID de la compagnie associée
    date_creation: datetime
    date_modification: datetime
    est_actif: bool = True

    class Config:
        from_attributes = True


class AvanceResponse(BaseModel):
    id: str = Field(
        ...,
        description="Identifiant unique de l'avance",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    employe_id: str  # UUID
    montant: float
    date: datetime
    motif: Optional[str] = None
    date_echeance: Optional[datetime] = None  # When should it be repaid
    utilisateur_id: str  # UUID of the user who created the advance
    numero_piece_comptable: Optional[str] = None
    compagnie_id: str  # UUID de la compagnie associée
    date_creation: datetime
    date_modification: datetime
    est_actif: bool = True

    class Config:
        from_attributes = True