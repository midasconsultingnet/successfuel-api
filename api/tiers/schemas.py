from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class SoldeTiersResponse(BaseModel):
    id: UUID
    tiers_id: UUID
    station_id: UUID
    montant_initial: float
    montant_actuel: float
    devise: str
    date_derniere_mise_a_jour: Optional[datetime] = None
    
    class Config:
        from_attributes = True