from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class EtatInitialCuveUpdateRequest(BaseModel):
    hauteur_jauge_initiale: Optional[float] = Field(None, description="Hauteur de jauge initiale en cm")
    cout_moyen: Optional[float] = Field(None, description="Coût moyen pondéré")
    prix_vente: Optional[float] = Field(None, description="Prix de vente")
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock")