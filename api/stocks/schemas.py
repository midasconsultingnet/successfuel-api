from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import UUID
from datetime import datetime

class StockCarburantInitialCreate(BaseModel):
    cuve_id: UUID
    hauteur_jauge_initiale: float = Field(..., description="Hauteur de jauge initiale en cm")
    cout_moyen: Optional[float] = Field(None, description="Coût moyen pondéré initial")
    prix_vente: Optional[float] = Field(None, description="Prix de vente initial")
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock")


class StockInitialCreate(BaseModel):
    produit_id: UUID
    station_id: UUID
    quantite_theorique: float = Field(..., description="Quantité théorique initiale")
    quantite_reelle: float = Field(..., description="Quantité réelle initiale")
    cout_moyen_pondere: Optional[float] = Field(None, description="Coût moyen pondéré initial")


class StockInitialResponse(BaseModel):
    id: UUID
    produit_id: UUID
    station_id: UUID
    quantite_theorique: float
    quantite_reelle: float
    date_dernier_calcul: datetime
    cout_moyen_pondere: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockInitialUpdate(BaseModel):
    quantite_theorique: Optional[float] = Field(None, description="Quantité théorique mise à jour")
    quantite_reelle: Optional[float] = Field(None, description="Quantité réelle mise à jour")
    cout_moyen_pondere: Optional[float] = Field(None, description="Coût moyen pondéré mis à jour")


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
    produit_id: UUID
    station_id: UUID
    nouvelle_quantite_theorique: float = Field(..., description="Nouvelle quantité théorique après correction")
    nouvelle_quantite_reelle: float = Field(..., description="Nouvelle quantité réelle après correction")
    raison: str = Field(..., description="Raison de la correction")
    cout_moyen_pondere: Optional[float] = Field(None, description="Nouveau coût moyen pondéré après correction")