from pydantic import BaseModel, field_validator, Field
from typing import Optional
import uuid
from datetime import datetime

def uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

class StockInitialCreate(BaseModel):
    """Schéma pour la création d'un stock initial."""
    produit_id: str = Field(
        ...,
        description="Identifiant unique du produit",
        example="123e4567-e89b-12d3-a456-426614174000"
    )  # UUID
    station_id: str = Field(
        ...,
        description="Identifiant unique de la station",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID
    quantite_initiale: float = Field(
        ...,
        description="Quantité initiale du stock",
        ge=0,
        example=100.0
    )
    cout_unitaire: Optional[float] = Field(
        0.0,
        description="Coût unitaire du produit pour le calcul du coût moyen pondéré",
        ge=0,
        example=1500.0
    )
    date_stock_initial: Optional[str] = Field(
        None,
        description="Date du stock initial au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO


class StockInitialResponse(BaseModel):
    """Schéma de réponse pour un stock initial."""
    id: str = Field(
        ...,
        description="Identifiant unique du stock initial",
        example="123e4567-e89b-12d3-a456-426614174002"
    )  # UUID
    produit_id: str = Field(
        ...,
        description="Identifiant unique du produit associé",
        example="123e4567-e89b-12d3-a456-426614174000"
    )  # UUID
    station_id: str = Field(
        ...,
        description="Identifiant unique de la station associée",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID
    quantite: float = Field(
        ...,
        description="Quantité du stock initial",
        ge=0,
        example=100.0
    )
    date_creation: Optional[str] = Field(
        None,
        description="Date de création du stock initial au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO

    @field_validator('id', 'produit_id', 'station_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('date_creation', mode='before')
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            # Ensure it's timezone-aware, default to UTC if not
            if v.tzinfo is None:
                v = v.replace(tzinfo=datetime.timezone.utc)
            return v.isoformat()
        return v

    model_config = {'from_attributes': True}