from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AchatCarburantCreate(BaseModel):
    """Schéma pour créer un achat de carburant."""
    fournisseur_id: str = Field(
        ...,
        description="Identifiant unique du fournisseur",
        example="123e4567-e89b-12d3-a456-426614174000"
    )  # UUID
    date_achat: datetime = Field(
        ...,
        description="Date de l'achat au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )
    numero_bl: Optional[str] = Field(
        None,
        description="Numéro du bon de livraison",
        example="BL-2023-12-001"
    )
    numero_facture: Optional[str] = Field(
        None,
        description="Numéro de la facture",
        example="FAC-2023-12-001"
    )
    montant_total: float = Field(
        ...,
        description="Montant total de l'achat",
        ge=0,
        example=2500000.0
    )
    station_id: str = Field(
        ...,
        description="Identifiant unique de la station",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID
    utilisateur_id: str = Field(
        ...,
        description="Identifiant unique de l'utilisateur effectuant l'achat",
        example="123e4567-e89b-12d3-a456-426614174002"
    )  # UUID

class AchatCarburantUpdate(BaseModel):
    """Schéma pour la mise à jour d'un achat de carburant."""
    numero_bl: Optional[str] = Field(
        None,
        description="Numéro du bon de livraison",
        example="BL-2023-12-001"
    )
    numero_facture: Optional[str] = Field(
        None,
        description="Numéro de la facture",
        example="FAC-2023-12-001"
    )
    montant_total: Optional[float] = Field(
        None,
        description="Montant total de l'achat",
        ge=0,
        example=2500000.0
    )
    statut: Optional[str] = Field(
        None,
        description="Statut de l'achat (brouillon, validé, facturé, annulé)",
        example="validé"
    )  # brouillon, validé, facturé, annulé
    utilisateur_id: Optional[str] = Field(
        None,
        description="Identifiant unique de l'utilisateur effectuant l'achat",
        example="123e4567-e89b-12d3-a456-426614174002"
    )

class LigneAchatCarburantCreate(BaseModel):
    """Schéma pour créer une ligne d'achat de carburant."""
    achat_carburant_id: str = Field(
        ...,
        description="Identifiant de l'achat de carburant auquel la ligne est associée",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    carburant_id: str = Field(
        ...,
        description="Identifiant du type de carburant",
        example="123e4567-e89b-12d3-a456-426614174004"
    )  # UUID
    quantite: float = Field(
        ...,
        description="Quantité de carburant",
        ge=0,
        example=1000.0
    )
    prix_unitaire: float = Field(
        ...,
        description="Prix unitaire du carburant",
        ge=0,
        example=1500.0
    )
    montant: float = Field(
        ...,
        description="Montant total pour cette ligne",
        ge=0,
        example=1500000.0
    )
    cuve_id: str = Field(
        ...,
        description="Identifiant unique de la cuve de destination",
        example="123e4567-e89b-12d3-a456-426614174005"
    )  # UUID

class LigneAchatCarburantUpdate(BaseModel):
    """Schéma pour la mise à jour d'une ligne d'achat de carburant."""
    quantite: Optional[float] = Field(
        None,
        description="Quantité de carburant",
        ge=0,
        example=1000.0
    )
    prix_unitaire: Optional[float] = Field(
        None,
        description="Prix unitaire du carburant",
        ge=0,
        example=1500.0
    )
    montant: Optional[float] = Field(
        None,
        description="Montant total pour cette ligne",
        ge=0,
        example=1500000.0
    )

class CompensationFinanciereCreate(BaseModel):
    """Schéma pour créer une compensation financière."""
    achat_carburant_id: str = Field(
        ...,
        description="Identifiant de l'achat de carburant concerné par la compensation",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    type_compensation: str = Field(
        ...,
        description="Type de compensation ('avoir_reçu' ou 'avoir_dû')",
        example="avoir_reçu"
    )  # "avoir_reçu", "avoir_dû"
    quantite_theorique: float = Field(
        ...,
        description="Quantité théorique prévue dans l'achat",
        ge=0,
        example=1000.0
    )
    quantite_reelle: float = Field(
        ...,
        description="Quantité réellement livrée",
        ge=0,
        example=950.0
    )
    difference: float = Field(
        ...,
        description="Différence entre la quantité réelle et la quantité théorique",
        example=50.0
    )
    montant_compensation: float = Field(
        ...,
        description="Montant de la compensation",
        ge=0,
        example=75000.0
    )
    motif: Optional[str] = Field(
        None,
        description="Motif de la compensation",
        example="Perte en transit"
    )

class CompensationFinanciereUpdate(BaseModel):
    """Schéma pour la mise à jour d'une compensation financière."""
    statut: Optional[str] = Field(
        None,
        description="Statut de la compensation (émis, utilisé, partiellement_utilisé, expiré)",
        example="émis"
    )  # émis, utilisé, partiellement_utilisé, expiré
    motif: Optional[str] = Field(
        None,
        description="Motif de la compensation",
        example="Perte en transit"
    )

class AvoirCompensationCreate(BaseModel):
    """Schéma pour créer un avoir de compensation."""
    compensation_financiere_id: str = Field(
        ...,
        description="Identifiant de la compensation financière à laquelle l'avoir est lié",
        example="123e4567-e89b-12d3-a456-426614174006"
    )  # UUID
    tiers_id: str = Field(
        ...,
        description="Identifiant du tiers (fournisseur ou client) concerné",
        example="123e4567-e89b-12d3-a456-426614174007"
    )  # UUID
    montant: float = Field(
        ...,
        description="Montant de l'avoir",
        ge=0,
        example=75000.0
    )
    motif: str = Field(
        ...,
        description="Motif de l'avoir de compensation",
        example="Perte en transit"
    )
    utilisateur_emission_id: str = Field(
        ...,
        description="Identifiant de l'utilisateur ayant émis l'avoir",
        example="123e4567-e89b-12d3-a456-426614174002"
    )  # UUID