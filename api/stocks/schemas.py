from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import UUID
from datetime import datetime

class StockCarburantInitialCreate(BaseModel):
    cuve_id: UUID
    hauteur_jauge_initiale: float = Field(..., description="Hauteur de jauge initiale en cm")
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock")


class StockInitialCreate(BaseModel):
    produit_id: UUID
    station_id: UUID
    quantite_initiale: float = Field(..., description="Quantité initiale du stock")
    cout_unitaire: float = Field(..., description="Coût unitaire du produit")
    prix_vente: Optional[float] = Field(None, description="Prix de vente du produit")
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock")
    date_stock_initial: Optional[datetime] = Field(None, description="Date du stock initial")


class StockInitialResponse(BaseModel):
    id: UUID
    produit_id: UUID
    station_id: UUID
    quantite: float
    cout_unitaire: Optional[float] = None
    prix_vente: Optional[float] = None
    seuil_stock_min: Optional[float] = None
    date_creation: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class StockInitialUpdate(BaseModel):
    quantite_initiale: Optional[float] = Field(None, description="Quantité initiale mise à jour")
    cout_unitaire: Optional[float] = Field(None, description="Coût unitaire mis à jour")
    prix_vente: Optional[float] = Field(None, description="Prix de vente mis à jour")
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock mis à jour")


class MouvementStockResponse(BaseModel):
    id: UUID
    produit_id: UUID
    station_id: UUID
    type_mouvement: str  # 'entree', 'sortie', 'ajustement_positif', 'ajustement_negatif'
    quantite: float
    date_mouvement: datetime
    utilisateur_id: UUID
    description: Optional[str] = None
    reference_origine: Optional[str] = None
    module_origine: Optional[str] = None
    statut: str = "valide"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockInitialCorrection(BaseModel):
    quantite_initiale: float = Field(..., description="Quantité initiale après correction")
    cout_unitaire: float = Field(..., description="Coût unitaire après correction")
    prix_vente: Optional[float] = Field(None, description="Prix de vente après correction")
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock après correction")
    raison: str = Field(..., description="Raison de la correction")