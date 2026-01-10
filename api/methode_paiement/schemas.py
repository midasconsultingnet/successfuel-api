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
    pass

class MethodePaiementUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    type_paiement: Optional[str] = None
    actif: Optional[bool] = None

class MethodePaiementResponse(MethodePaiementBase):
    id: uuid.UUID
    tresorerie_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TresorerieMethodePaiementBase(BaseModel):
    tresorerie_id: uuid.UUID
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

class TresorerieMethodePaiementDissocier(TresorerieMethodePaiementBase):
    pass

# Schéma pour la réponse avec les informations détaillées de la trésorerie
class TresorerieInfo(BaseModel):
    id: uuid.UUID
    nom: str
    type: str
    solde_initial: float
    devise: str
    statut: str
    compagnie_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class MethodePaiementTresorerieResponse(MethodePaiementBase):
    id: uuid.UUID
    tresorerie_id: Optional[uuid.UUID] = None
    tresorerie_info: Optional[TresorerieInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True