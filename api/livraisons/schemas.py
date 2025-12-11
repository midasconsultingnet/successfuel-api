from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LivraisonCreate(BaseModel):
    cuve_id: str  # UUID
    carburant_id: str  # UUID
    quantite_livree: int  # in liters
    date: datetime
    fournisseur_id: Optional[str] = None  # Optional - supplier of the delivery
    numero_bl: Optional[str] = None  # Delivery note number
    numero_facture: Optional[str] = None  # Invoice number
    prix_unitaire: Optional[float] = None  # Price per liter
    jauge_avant: Optional[int] = None  # Tank level before delivery
    jauge_apres: Optional[int] = None  # Tank level after delivery
    utilisateur_id: str  # UUID of the user who recorded the delivery
    commentaires: Optional[str] = None

class LivraisonUpdate(BaseModel):
    date: Optional[datetime] = None
    fournisseur_id: Optional[str] = None
    numero_bl: Optional[str] = None
    numero_facture: Optional[str] = None
    prix_unitaire: Optional[float] = None
    jauge_avant: Optional[int] = None
    jauge_apres: Optional[int] = None
    commentaires: Optional[str] = None