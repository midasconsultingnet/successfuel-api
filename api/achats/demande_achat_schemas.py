from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid


class StatutDemande(str, Enum):
    EN_ATTENTE = "en_attente"
    APPROUVEE = "approuvee"
    REJETEE = "rejetee"


class LigneDemandeAchatCreate(BaseModel):
    designation: str = Field(..., max_length=255)
    description: Optional[str] = None
    quantite: int = Field(..., gt=0)
    prix_unitaire: float = Field(..., ge=0)
    unite: Optional[str] = Field(default="unité", max_length=20)
    produit_id: Optional[uuid.UUID] = None
    montant_total: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Calculer montant_total si ce n'est pas fourni explicitement
        if self.montant_total is None and self.quantite is not None and self.prix_unitaire is not None:
            self.montant_total = self.quantite * self.prix_unitaire

    class Config:
        from_attributes = True


class LigneDemandeAchatResponse(BaseModel):
    id: uuid.UUID
    designation: str
    description: Optional[str]
    quantite: int
    prix_unitaire: float
    unite: str
    montant_total: float
    produit_id: Optional[uuid.UUID]
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True


class DemandeAchatCreate(BaseModel):
    objet: str
    tiers_id: uuid.UUID
    lignes_demande: List[LigneDemandeAchatCreate]

    class Config:
        from_attributes = True


class DemandeAchatUpdate(BaseModel):
    objet: Optional[str] = None
    statut: Optional[StatutDemande] = None
    lignes_demande: Optional[List[LigneDemandeAchatCreate]] = None

    class Config:
        from_attributes = True


class DemandeAchatResponse(BaseModel):
    id: uuid.UUID
    numero: str
    objet: str
    statut: StatutDemande
    date_demande: datetime
    date_validation: Optional[datetime]
    montant_total: float
    utilisateur_id: uuid.UUID
    tiers_id: uuid.UUID
    lignes_demande: List[LigneDemandeAchatResponse]

    class Config:
        from_attributes = True