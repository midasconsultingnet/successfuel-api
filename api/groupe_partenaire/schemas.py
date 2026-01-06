from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


class GroupePartenaireBase(BaseModel):
    nom: str = Field(..., description="Nom du groupe partenaire", example="Groupe Distributeur A")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"type": "distributeur", "region": "Dakar"})


class GroupePartenaireCreate(GroupePartenaireBase):
    pass


class GroupePartenaireUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom du groupe partenaire", example="Groupe Distributeur A")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"type": "distributeur", "region": "Dakar"})


class GroupePartenaireResponse(GroupePartenaireBase):
    id: uuid.UUID = Field(..., description="Identifiant unique du groupe partenaire", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    created_at: datetime = Field(..., description="Date de création du groupe partenaire", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True