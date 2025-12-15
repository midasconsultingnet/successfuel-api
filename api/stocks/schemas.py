from pydantic import BaseModel, field_validator
from typing import Optional
import uuid
from datetime import datetime

def uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

class StockInitialCreate(BaseModel):
    produit_id: str  # UUID
    station_id: str  # UUID
    quantite_initiale: float
    cout_unitaire: Optional[float] = 0.0
    date_stock_initial: Optional[str] = None  # Format ISO

class StockInitialResponse(BaseModel):
    id: str  # UUID
    produit_id: str  # UUID
    station_id: str  # UUID
    quantite: float
    date_creation: Optional[str] = None  # Format ISO

    @field_validator('id', 'produit_id', 'station_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('date_creation', mode='before')
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    model_config = {'from_attributes': True}