from pydantic import BaseModel
from typing import Optional

class FamilleProduitCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    code: str
    famille_parente_id: Optional[int] = None

class FamilleProduitUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    famille_parente_id: Optional[int] = None

class ProduitCreate(BaseModel):
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[int] = 0
    famille_id: Optional[int] = None
    has_stock: Optional[bool] = True  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = None  # ISO format date

class ProduitUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    prix_vente: Optional[float] = None
    seuil_stock_min: Optional[int] = None
    famille_id: Optional[int] = None
    has_stock: Optional[bool] = None
    date_limite_consommation: Optional[str] = None

class LotCreate(BaseModel):
    produit_id: str  # UUID
    numero_lot: str
    quantite: int
    date_production: Optional[str] = None  # Format ISO
    date_peremption: Optional[str] = None  # Format ISO

class LotUpdate(BaseModel):
    quantite: Optional[int] = None
    date_peremption: Optional[str] = None  # Format ISO

class LotResponse(BaseModel):
    id: str  # UUID
    produit_id: str  # UUID
    numero_lot: str
    quantite: int
    date_production: Optional[str] = None  # Format ISO
    date_peremption: Optional[str] = None  # Format ISO

class FamilleProduitResponse(BaseModel):
    id: str  # UUID
    nom: str
    description: Optional[str] = None
    code: str
    famille_parente_id: Optional[str] = None  # UUID

class ProduitResponse(BaseModel):
    id: str  # UUID
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[int] = 0
    famille_id: Optional[str] = None  # UUID
    has_stock: Optional[bool] = True  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = None  # ISO format date