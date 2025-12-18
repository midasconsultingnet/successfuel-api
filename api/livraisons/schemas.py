from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LivraisonCreate(BaseModel):
    cuve_id: str = Field(
        ...,
        description="Identifiant unique de la cuve qui reçoit la livraison de carburant",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    carburant_id: str = Field(
        ...,
        description="Identifiant unique du type de carburant livré",
        example="987fb8a6-c5b4-4a2d-bf6d-1e8f9a0c3b4d"
    )
    quantite_livree: int = Field(
        ...,
        ge=0,
        description="Quantité de carburant livrée en litres",
        example=5000
    )
    date: datetime = Field(
        ...,
        description="Date et heure de la livraison",
        example="2023-10-15T09:30:00"
    )
    fournisseur_id: Optional[str] = Field(
        None,
        description="Identifiant unique du fournisseur de la livraison",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    numero_bl: Optional[str] = Field(
        None,
        max_length=50,
        description="Numéro du bon de livraison",
        example="BL-2023-10-001"
    )
    numero_facture: Optional[str] = Field(
        None,
        max_length=50,
        description="Numéro de la facture associée à la livraison",
        example="FAC-2023-10-001"
    )
    prix_unitaire: Optional[float] = Field(
        None,
        ge=0,
        description="Prix unitaire du carburant en devise locale par litre",
        example=1.25
    )
    jauge_avant: Optional[int] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve avant la livraison (en litres)",
        example=2000
    )
    jauge_apres: Optional[int] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve après la livraison (en litres)",
        example=7000
    )
    utilisateur_id: str = Field(
        ...,
        description="Identifiant unique de l'utilisateur qui a enregistré la livraison",
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef"
    )
    commentaires: Optional[str] = Field(
        None,
        max_length=500,
        description="Commentaires ou notes supplémentaires sur la livraison",
        example="Livraison effectuée en semaine, surveillance renforcée requise"
    )

class LivraisonUpdate(BaseModel):
    date: Optional[datetime] = Field(
        None,
        description="Date et heure de la livraison",
        example="2023-10-15T09:30:00"
    )
    fournisseur_id: Optional[str] = Field(
        None,
        description="Identifiant unique du fournisseur de la livraison",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    numero_bl: Optional[str] = Field(
        None,
        max_length=50,
        description="Numéro du bon de livraison",
        example="BL-2023-10-001"
    )
    numero_facture: Optional[str] = Field(
        None,
        max_length=50,
        description="Numéro de la facture associée à la livraison",
        example="FAC-2023-10-001"
    )
    prix_unitaire: Optional[float] = Field(
        None,
        ge=0,
        description="Prix unitaire du carburant en devise locale par litre",
        example=1.25
    )
    jauge_avant: Optional[int] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve avant la livraison (en litres)",
        example=2000
    )
    jauge_apres: Optional[int] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve après la livraison (en litres)",
        example=7000
    )
    commentaires: Optional[str] = Field(
        None,
        max_length=500,
        description="Commentaires ou notes supplémentaires sur la livraison",
        example="Livraison effectuée en semaine, surveillance renforcée requise"
    )