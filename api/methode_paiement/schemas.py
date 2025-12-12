from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class MethodePaiementBase(BaseModel):
    nom: str
    description: Optional[str] = None
    type_paiement: str  # cash, cheque, virement, mobile_money, etc.
    actif: Optional[bool] = True

class MethodePaiementCreate(MethodePaiementBase):
    trésorerie_id: Optional[uuid.UUID] = None  # Peut être None pour les méthodes globales

class MethodePaiementUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    type_paiement: Optional[str] = None
    actif: Optional[bool] = None

class MethodePaiementResponse(MethodePaiementBase):
    id: uuid.UUID
    trésorerie_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TresorerieMethodePaiementBase(BaseModel):
    trésorerie_id: uuid.UUID
    methode_paiement_id: uuid.UUID
    actif: Optional[bool] = True

class TresorerieMethodePaiementCreate(TresorerieMethodePaiementBase):
    pass

class TresorerieMethodePaiementUpdate(BaseModel):
    actif: Optional[bool] = None

class TresorerieMethodePaiementResponse(TresorerieMethodePaiementBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True