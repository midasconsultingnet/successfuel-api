from pydantic import BaseModel, field_validator, Field
from typing import Optional
import uuid
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

def uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

class FamilleProduitCreate(BaseModel):
    nom: str = Field(..., description="Nom de la famille de produits", example="Lubrifiants")
    description: Optional[str] = Field(None, description="Description détaillée de la famille de produits", example="Tous les types de lubrifiants pour véhicules")
    code: str = Field(..., description="Code unique identifiant la famille de produits", example="LUB")
    famille_parente_id: Optional[int | str] = Field(None, description="Identifiant de la famille parente (s'il existe), 0 signifie aucune parente")  # UUID or 0 for no parent

    @field_validator('famille_parente_id')
    @classmethod
    def validate_uuid(cls, v):
        if v is not None:
            if v == 0:
                return None
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError('famille_parente_id must be a valid UUID')
        return v

class FamilleProduitUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom de la famille de produits", example="Lubrifiants")
    description: Optional[str] = Field(None, description="Description détaillée de la famille de produits", example="Tous les types de lubrifiants pour véhicules")
    code: Optional[str] = Field(None, description="Code unique identifiant la famille de produits", example="LUB")
    famille_parente_id: Optional[int | str] = Field(None, description="Identifiant de la famille parente (s'il existe), 0 signifie aucune parente")  # UUID or 0 for no parent

    @field_validator('famille_parente_id')
    @classmethod
    def validate_uuid(cls, v):
        if v is not None:
            if v == 0:
                return None
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError('famille_parente_id must be a valid UUID')
        return v

class ProduitCreate(BaseModel):
    nom: str = Field(..., description="Nom du produit", example="Huile moteur 15W40")
    code: str = Field(..., description="Code unique identifiant le produit", example="HUI1540")
    description: Optional[str] = Field(None, description="Description détaillée du produit", example="Huile moteur pour véhicules diesel")
    unite_mesure: Optional[str] = Field("unité", description="Unité de mesure du produit", example="litre")
    type: str = Field(..., description="Type du produit (boutique, lubrifiant, gaz, service)", example="lubrifiant")
    prix_vente: float = Field(..., description="Prix de vente du produit", example=15.5)
    seuil_stock_min: Optional[float] = Field(0, description="Seuil minimum de stock du produit", example=10)
    famille_id: Optional[str] = Field(None, description="Identifiant de la famille de produits à laquelle appartient le produit")  # UUID
    has_stock: Optional[bool] = Field(True, description="Indique si le produit est géré en stock (True) ou s'il s'agit d'un service (False)")  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = Field(None, description="Date limite de consommation du produit (format ISO 8601)", example="2024-12-31")  # ISO format date

    @field_validator('seuil_stock_min', mode='before')
    @classmethod
    def validate_stock_fields_for_services(cls, v, info):
        # Récupérer le type du produit s'il est disponible
        if info.data.get('type') == 'service' and v is not None and v != 0:
            raise ValueError(f"Ce champ ne devrait pas avoir de valeur pour les produits de type service")
        return v

    @field_validator('has_stock', mode='before')
    @classmethod
    def validate_has_stock_consistency(cls, v, info):
        # Si le type est 'service', has_stock devrait être False
        if info.data.get('type') == 'service' and v != False:
            raise ValueError("Les produits de type service ne devraient pas avoir de stock (has_stock = False)")
        return v

    @field_validator('date_limite_consommation', mode='before')
    @classmethod
    def validate_date_limite_consommation(cls, v):
        if v == "":
            return None
        if v == "string":  # Pour éviter la valeur par défaut de certaines interfaces
            return None
        if v is not None:
            # Vérifier si c'est une date valide (format ISO 8601)
            from datetime import datetime
            try:
                # Essayer de parser la date pour s'assurer qu'elle est valide
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("La date limite de consommation doit être au format ISO 8601 (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)")
        return v

class ProduitUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom du produit", example="Huile moteur 15W40")
    description: Optional[str] = Field(None, description="Description détaillée du produit", example="Huile moteur pour véhicules diesel")
    prix_vente: Optional[float] = Field(None, description="Prix de vente du produit", example=15.5)
    seuil_stock_min: Optional[float] = Field(None, description="Seuil minimum de stock du produit", example=10)
    famille_id: Optional[str] = Field(None, description="Identifiant de la famille de produits à laquelle appartient le produit")  # UUID
    has_stock: Optional[bool] = Field(None, description="Indique si le produit est géré en stock (True) ou s'il s'agit d'un service (False)")
    date_limite_consommation: Optional[str] = Field(None, description="Date limite de consommation du produit (format ISO 8601)", example="2024-12-31")

    @field_validator('seuil_stock_min', mode='before')
    @classmethod
    def validate_stock_fields_for_services(cls, v, info):
        # Récupérer le type du produit s'il est disponible
        if info.data.get('type') == 'service' and v is not None and v != 0:
            raise ValueError(f"Ce champ ne devrait pas avoir de valeur pour les produits de type service")
        return v

    @field_validator('has_stock', mode='before')
    @classmethod
    def validate_has_stock_consistency(cls, v, info):
        # Si le type est 'service', has_stock devrait être False
        if info.data.get('type') == 'service' and v != False:
            raise ValueError("Les produits de type service ne devraient pas avoir de stock (has_stock = False)")
        return v

    @field_validator('date_limite_consommation', mode='before')
    @classmethod
    def validate_date_limite_consommation(cls, v):
        if v == "":
            return None
        if v == "string":  # Pour éviter la valeur par défaut de certaines interfaces
            return None
        if v is not None:
            # Vérifier si c'est une date valide (format ISO 8601)
            from datetime import datetime
            try:
                # Essayer de parser la date pour s'assurer qu'elle est valide
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("La date limite de consommation doit être au format ISO 8601 (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)")
        return v

class LotCreate(BaseModel):
    produit_id: str = Field(..., description="Identifiant du produit auquel le lot est associé", example="550e8400-e29b-41d4-a716-446655440000")  # UUID
    numero_lot: str = Field(..., description="Numéro identifiant le lot", example="LOT20231201001")
    quantite: int = Field(..., description="Quantité du lot", example=100)
    date_production: Optional[str] = Field(None, description="Date de production du lot (format ISO 8601)", example="2023-12-01")  # Format ISO
    date_peremption: Optional[str] = Field(None, description="Date de péremption du lot (format ISO 8601)", example="2024-12-01")  # Format ISO

class LotUpdate(BaseModel):
    quantite: Optional[int] = Field(None, description="Quantité du lot", example=100)
    date_peremption: Optional[str] = Field(None, description="Date de péremption du lot (format ISO 8601)", example="2024-12-01")  # Format ISO

class LotResponse(BaseModel):
    id: str = Field(..., description="Identifiant unique du lot", example="550e8400-e29b-41d4-a716-446655440000")  # UUID
    produit_id: str = Field(..., description="Identifiant du produit auquel le lot est associé", example="550e8400-e29b-41d4-a716-446655440001")  # UUID
    numero_lot: str = Field(..., description="Numéro identifiant le lot", example="LOT20231201001")
    quantite: int = Field(..., description="Quantité du lot", example=100)
    date_production: Optional[str] = Field(None, description="Date de production du lot (format ISO 8601)", example="2023-12-01")  # Format ISO
    date_peremption: Optional[str] = Field(None, description="Date de péremption du lot (format ISO 8601)", example="2024-12-01")  # Format ISO

class FamilleProduitParent(BaseModel):
    id: str = Field(..., description="Identifiant unique de la famille de produits parente", example="550e8400-e29b-41d4-a716-446655440000")  # UUID
    nom: str = Field(..., description="Nom de la famille de produits parente", example="Lubrifiants")
    description: Optional[str] = Field(None, description="Description de la famille de produits parente", example="Tous les types de lubrifiants pour véhicules")
    code: str = Field(..., description="Code de la famille de produits parente", example="LUB")

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}

class FamilleProduitResponse(BaseModel):
    id: str = Field(..., description="Identifiant unique de la famille de produits", example="550e8400-e29b-41d4-a716-446655440000")  # UUID
    nom: str = Field(..., description="Nom de la famille de produits", example="Lubrifiants")
    description: Optional[str] = Field(None, description="Description de la famille de produits", example="Tous les types de lubrifiants pour véhicules")
    code: str = Field(..., description="Code de la famille de produits", example="LUB")
    famille_parente_id: Optional[str] = Field(None, description="Identifiant de la famille de produits parente", example="550e8400-e29b-41d4-a716-446655440001")  # UUID
    famille_parente: Optional[FamilleProduitParent] = Field(None, description="Informations de la famille de produits parente")  # Informations de la famille parente

    @field_validator('id', 'famille_parente_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}

class ProduitResponse(BaseModel):
    id: str = Field(..., description="Identifiant unique du produit", example="550e8400-e29b-41d4-a716-446655440000")  # UUID
    nom: str = Field(..., description="Nom du produit", example="Huile moteur 15W40")
    code: str = Field(..., description="Code unique identifiant le produit", example="HUI1540")
    description: Optional[str] = Field(None, description="Description détaillée du produit", example="Huile moteur pour véhicules diesel")
    unite_mesure: Optional[str] = Field("unité", description="Unité de mesure du produit", example="litre")
    type: str = Field(..., description="Type du produit (boutique, lubrifiant, gaz, service)", example="lubrifiant")  # boutique, lubrifiant, gaz, service
    prix_vente: float = Field(..., description="Prix de vente du produit", example=15.5)
    seuil_stock_min: Optional[float] = Field(0, description="Seuil minimum de stock du produit", example=10)
    cout_moyen: Optional[float] = Field(0, description="Coût moyen du produit", example=10.2)
    famille_id: Optional[str] = Field(None, description="Identifiant de la famille de produits à laquelle appartient le produit", example="550e8400-e29b-41d4-a716-446655440001")  # UUID
    station_id: Optional[str] = Field(None, description="Identifiant de la station à laquelle est associé le produit", example="550e8400-e29b-41d4-a716-446655440002")  # UUID
    has_stock: Optional[bool] = Field(True, description="Indique si le produit est géré en stock (True) ou s'il s'agit d'un service (False)")  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = Field(None, description="Date limite de consommation du produit (format ISO 8601)", example="2024-12-31")  # ISO format date

    @field_validator('id', 'famille_id', 'station_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}


class ProduitStockResponse(BaseModel):
    id: str = Field(..., description="Identifiant unique du produit", example="550e8400-e29b-41d4-a716-446655440000")  # UUID
    nom: str = Field(..., description="Nom du produit", example="Huile moteur 15W40")
    code: str = Field(..., description="Code unique identifiant le produit", example="HUI1540")
    description: Optional[str] = Field(None, description="Description détaillée du produit", example="Huile moteur pour véhicules diesel")
    unite_mesure: Optional[str] = Field("unité", description="Unité de mesure du produit", example="litre")
    type: str = Field(..., description="Type du produit (boutique, lubrifiant, gaz, service)", example="lubrifiant")  # boutique, lubrifiant, gaz, service
    prix_vente: float = Field(..., description="Prix de vente du produit", example=15.5)
    seuil_stock_min: Optional[float] = Field(0, description="Seuil minimum de stock du produit", example=10)
    cout_moyen: Optional[float] = Field(0, description="Coût moyen du produit", example=10.2)
    famille_id: Optional[str] = Field(None, description="Identifiant de la famille de produits à laquelle appartient le produit", example="550e8400-e29b-41d4-a716-446655440001")  # UUID
    station_id: Optional[str] = Field(None, description="Identifiant de la station à laquelle est associé le produit", example="550e8400-e29b-41d4-a716-446655440002")  # UUID
    has_stock: Optional[bool] = Field(True, description="Indique si le produit est géré en stock (True) ou s'il s'agit d'un service (False)")  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = Field(None, description="Date limite de consommation du produit (format ISO 8601)", example="2024-12-31")  # ISO format date
    quantite_stock: Optional[float] = Field(0, description="Quantité disponible en stock du produit", example=50.0)  # Quantité disponible en stock

    @field_validator('id', 'famille_id', 'station_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}