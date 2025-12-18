from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class LotBase(BaseModel):
    """Schéma de base pour un lot de produits."""
    produit_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique du produit associé au lot",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    station_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la station où se trouve le lot",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    numero_lot: str = Field(
        ...,
        description="Numéro de lot pour identifier le groupe de produits",
        max_length=100,
        example="LOT-2023-SERIE-A"
    )
    date_fabrication: Optional[datetime] = Field(
        None,
        description="Date de fabrication du lot au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-01-15T09:30:00.000000"
    )
    date_limite_consommation: Optional[datetime] = Field(
        None,
        description="Date limite de consommation ou de péremption du lot au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2024-01-15T09:30:00.000000"
    )
    quantite: float = Field(
        ...,
        description="Quantité totale du lot",
        ge=0,
        example=500.0
    )
    statut: Optional[str] = Field(
        "actif",
        description="Statut du lot (actif, expiré, vendu, etc.)",
        example="actif"
    )

    class Config:
        from_attributes = True


class LotCreate(LotBase):
    """Schéma pour la création d'un lot."""
    pass


class LotUpdate(BaseModel):
    """Schéma pour la mise à jour partielle d'un lot."""
    numero_lot: Optional[str] = Field(
        None,
        description="Numéro de lot pour identifier le groupe de produits",
        max_length=100,
        example="LOT-2023-SERIE-A"
    )
    date_fabrication: Optional[datetime] = Field(
        None,
        description="Date de fabrication du lot au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-01-15T09:30:00.000000"
    )
    date_limite_consommation: Optional[datetime] = Field(
        None,
        description="Date limite de consommation ou de péremption du lot au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2024-01-15T09:30:00.000000"
    )
    quantite: Optional[float] = Field(
        None,
        description="Quantité totale du lot",
        ge=0,
        example=500.0
    )
    statut: Optional[str] = Field(
        None,
        description="Statut du lot (actif, expiré, vendu, etc.)",
        example="actif"
    )

    class Config:
        from_attributes = True


class LotResponse(LotBase):
    """Schéma de réponse pour un lot avec des informations supplémentaires."""
    id: uuid.UUID = Field(
        ...,
        description="Identifiant unique du lot",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    created_at: datetime = Field(
        ...,
        description="Date de création du lot au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-01-15T09:30:00.000000"
    )

    class Config:
        from_attributes = True