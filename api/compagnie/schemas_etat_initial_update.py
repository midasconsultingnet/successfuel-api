from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class EtatInitialCuveUpdateRequest(BaseModel):
    cuve_id: Optional[UUID] = None
    hauteur_jauge_initiale: Optional[float] = Field(None, description="Hauteur de jauge initiale en cm")
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock")