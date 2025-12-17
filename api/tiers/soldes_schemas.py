from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum

class TypeSoldeInitial(str, Enum):
    dette = "dette"
    creance = "creance"

class SoldeTiersBase(BaseModel):
    tiers_id: uuid.UUID
    station_id: uuid.UUID
    montant_initial: float
    devise: Optional[str] = "XOF"
    date_derniere_mise_a_jour: Optional[datetime] = None

    class Config:
        from_attributes = True

class SoldeTiersCreate(BaseModel):
    montant_initial: float
    type_solde_initial: TypeSoldeInitial
    devise: Optional[str] = "XOF"

    class Config:
        from_attributes = True

class SoldeTiersUpdate(BaseModel):
    montant_initial: Optional[float] = None
    montant_actuel: Optional[float] = None

    class Config:
        from_attributes = True

class SoldeTiersResponse(SoldeTiersBase):
    id: uuid.UUID
    tiers_id: uuid.UUID
    montant_actuel: float
    date_derniere_mise_a_jour: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MouvementTiersBase(BaseModel):
    tiers_id: uuid.UUID
    type_mouvement: str  # 'débit' ou 'crédit'
    montant: float
    date_mouvement: datetime
    description: Optional[str] = None
    module_origine: str
    reference_origine: str
    utilisateur_id: uuid.UUID
    numero_piece_comptable: Optional[str] = None
    statut: Optional[str] = 'validé'

    class Config:
        from_attributes = True

class MouvementTiersCreate(MouvementTiersBase):
    pass

class MouvementTiersUpdate(BaseModel):
    type_mouvement: Optional[str] = None
    montant: Optional[float] = None
    description: Optional[str] = None
    numero_piece_comptable: Optional[str] = None
    statut: Optional[str] = None

    class Config:
        from_attributes = True

class MouvementTiersResponse(MouvementTiersBase):
    id: uuid.UUID

    class Config:
        from_attributes = True