from pydantic import BaseModel, field_validator, Field
from typing import Optional
import uuid
from datetime import datetime

def uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

class StockInitialCorrection(BaseModel):
    """Schéma pour la correction d'un stock initial."""
    quantite_initiale: float = Field(
        ...,
        description="Nouvelle quantité du stock initial après correction",
        ge=0,
        example=100.0
    )
    cout_unitaire: Optional[float] = Field(
        0.0,
        description="Coût unitaire du produit pour le calcul du coût moyen pondéré",
        ge=0,
        example=1500.0
    )
    prix_vente: Optional[float] = Field(
        None,
        description="Prix de vente du produit dans cette station",
        ge=0,
        example=15.5
    )
    seuil_stock_min: Optional[float] = Field(
        None,
        description="Seuil minimum de stock",
        ge=0,
        example=10.0
    )


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
    prix_vente: Optional[float] = Field(
        None,
        description="Prix de vente du produit dans cette station",
        ge=0,
        example=15.5
    )
    seuil_stock_min: Optional[float] = Field(
        None,
        description="Seuil minimum de stock",
        ge=0,
        example=10.0
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
                import datetime as dt
                v = v.replace(tzinfo=dt.timezone.utc)
            return v.isoformat()
        return v

    model_config = {'from_attributes': True}


class MouvementStockResponse(BaseModel):
    """Schéma de réponse pour un mouvement de stock."""
    id: str = Field(
        ...,
        description="Identifiant unique du mouvement de stock",
        example="123e4567-e89b-12d3-a456-426614174000"
    )  # UUID
    produit_id: str = Field(
        ...,
        description="Identifiant unique du produit concerné",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID
    station_id: str = Field(
        ...,
        description="Identifiant unique de la station concernée",
        example="123e4567-e89b-12d3-a456-426614174002"
    )  # UUID
    type_mouvement: str = Field(
        ...,
        description="Type de mouvement (entrée, sortie, ajustement_plus, ajustement_moins, stock_initial, etc.)",
        example="entree"
    )
    quantite: float = Field(
        ...,
        description="Quantité concernée par le mouvement (positive pour les entrées, négative pour les sorties)",
        example=100.0
    )
    date_mouvement: Optional[str] = Field(
        None,
        description="Date du mouvement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO
    description: Optional[str] = Field(
        None,
        description="Description optionnelle du mouvement",
        example="Mouvement d'entrée de stock"
    )
    module_origine: str = Field(
        ...,
        description="Module d'origine du mouvement",
        example="achat"
    )
    reference_origine: str = Field(
        ...,
        description="Référence d'origine du mouvement",
        example="ACH-001"
    )
    utilisateur_id: str = Field(
        ...,
        description="Identifiant de l'utilisateur à l'origine du mouvement",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    cout_unitaire: Optional[float] = Field(
        None,
        description="Coût unitaire du produit au moment du mouvement",
        ge=0,
        example=1500.0
    )
    statut: str = Field(
        ...,
        description="Statut du mouvement (validé, annulé, etc.)",
        example="validé"
    )
    transaction_source_id: Optional[str] = Field(
        None,
        description="Identifiant de la transaction source",
        example="123e4567-e89b-12d3-a456-426614174004"
    )  # UUID
    type_transaction_source: Optional[str] = Field(
        None,
        description="Type de la transaction source",
        example="achat"
    )
    mouvement_origine_id: Optional[str] = Field(
        None,
        description="Identifiant du mouvement original en cas d'annulation",
        example="123e4567-e89b-12d3-a456-426614174005"
    )  # UUID
    created_at: Optional[str] = Field(
        None,
        description="Date de création du mouvement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO
    updated_at: Optional[str] = Field(
        None,
        description="Date de dernière mise à jour du mouvement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO
    est_actif: bool = Field(
        ...,
        description="Indique si le mouvement est actif",
        example=True
    )

    @field_validator('id', 'produit_id', 'station_id', 'utilisateur_id', 'transaction_source_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('date_mouvement', 'created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            # Ensure it's timezone-aware, default to UTC if not
            if v.tzinfo is None:
                import datetime as dt
                v = v.replace(tzinfo=dt.timezone.utc)
            return v.isoformat()
        return v

    model_config = {'from_attributes': True}


class StockProduitUpdate(BaseModel):
    """Schéma pour la mise à jour d'un stock de produit."""
    prix_vente: Optional[float] = Field(
        None,
        description="Prix de vente du produit au stock",
        ge=0,
        example=15.5
    )
    seuil_stock_min: Optional[float] = Field(
        None,
        description="Seuil minimum de stock",
        ge=0,
        example=10.0
    )


class StockProduitResponse(BaseModel):
    """Schéma de réponse pour un stock de produit."""
    id: str = Field(
        ...,
        description="Identifiant unique du stock",
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
    quantite_theorique: float = Field(
        ...,
        description="Quantité théorique en stock",
        ge=0,
        example=50.0
    )
    quantite_reelle: float = Field(
        ...,
        description="Quantité réelle en stock",
        ge=0,
        example=48.0
    )
    prix_vente: float = Field(
        ...,
        description="Prix de vente du produit au stock",
        ge=0,
        example=15.5
    )
    seuil_stock_min: float = Field(
        ...,
        description="Seuil minimum de stock",
        ge=0,
        example=10.0
    )
    date_dernier_calcul: Optional[str] = Field(
        None,
        description="Date du dernier calcul de stock au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO

    @field_validator('id', 'produit_id', 'station_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('date_dernier_calcul', mode='before')
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            # Ensure it's timezone-aware, default to UTC if not
            if v.tzinfo is None:
                import datetime as dt
                v = v.replace(tzinfo=dt.timezone.utc)
            return v.isoformat()
        return v

    model_config = {'from_attributes': True}


class MouvementStockResponse(BaseModel):
    """Schéma de réponse pour un mouvement de stock."""
    id: str = Field(
        ...,
        description="Identifiant unique du mouvement de stock",
        example="123e4567-e89b-12d3-a456-426614174000"
    )  # UUID
    produit_id: str = Field(
        ...,
        description="Identifiant unique du produit concerné",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID
    station_id: str = Field(
        ...,
        description="Identifiant unique de la station concernée",
        example="123e4567-e89b-12d3-a456-426614174002"
    )  # UUID
    type_mouvement: str = Field(
        ...,
        description="Type de mouvement (entrée, sortie, ajustement_plus, ajustement_moins, stock_initial, etc.)",
        example="entree"
    )
    quantite: float = Field(
        ...,
        description="Quantité concernée par le mouvement (positive pour les entrées, négative pour les sorties)",
        example=100.0
    )
    date_mouvement: Optional[str] = Field(
        None,
        description="Date du mouvement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO
    description: Optional[str] = Field(
        None,
        description="Description optionnelle du mouvement",
        example="Mouvement d'entrée de stock"
    )
    module_origine: str = Field(
        ...,
        description="Module d'origine du mouvement",
        example="achat"
    )
    reference_origine: str = Field(
        ...,
        description="Référence d'origine du mouvement",
        example="ACH-001"
    )
    utilisateur_id: str = Field(
        ...,
        description="Identifiant de l'utilisateur à l'origine du mouvement",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    cout_unitaire: Optional[float] = Field(
        None,
        description="Coût unitaire du produit au moment du mouvement",
        ge=0,
        example=1500.0
    )
    statut: str = Field(
        ...,
        description="Statut du mouvement (validé, annulé, etc.)",
        example="validé"
    )
    transaction_source_id: Optional[str] = Field(
        None,
        description="Identifiant de la transaction source",
        example="123e4567-e89b-12d3-a456-426614174004"
    )  # UUID
    type_transaction_source: Optional[str] = Field(
        None,
        description="Type de la transaction source",
        example="achat"
    )
    mouvement_origine_id: Optional[str] = Field(
        None,
        description="Identifiant du mouvement original en cas d'annulation",
        example="123e4567-e89b-12d3-a456-426614174005"
    )  # UUID
    created_at: Optional[str] = Field(
        None,
        description="Date de création du mouvement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO
    updated_at: Optional[str] = Field(
        None,
        description="Date de dernière mise à jour du mouvement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )  # Format ISO
    est_actif: bool = Field(
        ...,
        description="Indique si le mouvement est actif",
        example=True
    )

    @field_validator('id', 'produit_id', 'station_id', 'utilisateur_id', 'transaction_source_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('date_mouvement', 'created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            # Ensure it's timezone-aware, default to UTC if not
            if v.tzinfo is None:
                import datetime as dt
                v = v.replace(tzinfo=dt.timezone.utc)
            return v.isoformat()
        return v

    model_config = {'from_attributes': True}