from pydantic import BaseModel
from typing import Optional

class StockCreate(BaseModel):
    produit_id: str  # UUID
    station_id: str  # UUID
    quantite: int
    cuve_id: Optional[str] = None  # For fuel stocks

class StockUpdate(BaseModel):
    quantite: Optional[int] = None

class StockResponse(BaseModel):
    id: str  # UUID
    produit_id: str  # UUID
    station_id: str  # UUID
    quantite_theorique: float
    quantite_reelle: float
    date_dernier_calcul: Optional[str] = None
    cout_moyen_pondere: float

class MouvementStockResponse(BaseModel):
    id: str  # UUID
    produit_id: str  # UUID
    station_id: str  # UUID
    type_mouvement: str  # "entree", "sortie", "ajustement"
    quantite: float
    date_mouvement: Optional[str] = None  # Format ISO
    description: Optional[str] = None
    module_origine: Optional[str] = None
    reference_origine: Optional[str] = None
    utilisateur_id: Optional[str] = None
    cout_unitaire: Optional[float] = None