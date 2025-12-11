from pydantic import BaseModel
from typing import Optional

class ParametreCreate(BaseModel):
    cle: str
    valeur: str
    description: Optional[str] = None
    compagnie_id: str  # UUID of the company

class ParametreUpdate(BaseModel):
    valeur: str
    description: Optional[str] = None

class SeuilCreate(BaseModel):
    nom: str
    valeur: float
    description: Optional[str] = None
    compagnie_id: str  # UUID of the company

class SeuilUpdate(BaseModel):
    valeur: float
    description: Optional[str] = None