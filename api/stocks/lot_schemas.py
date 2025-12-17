from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class LotBase(BaseModel):
    produit_id: uuid.UUID
    station_id: uuid.UUID
    numero_lot: str
    date_fabrication: Optional[datetime] = None
    date_limite_consommation: Optional[datetime] = None
    quantite: float
    statut: Optional[str] = "actif"

    class Config:
        from_attributes = True


class LotCreate(LotBase):
    pass


class LotUpdate(BaseModel):
    numero_lot: Optional[str] = None
    date_fabrication: Optional[datetime] = None
    date_limite_consommation: Optional[datetime] = None
    quantite: Optional[float] = None
    statut: Optional[str] = None

    class Config:
        from_attributes = True


class LotResponse(LotBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True