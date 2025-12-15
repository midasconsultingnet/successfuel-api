from pydantic import BaseModel, field_validator
from typing import Optional
import uuid
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

def uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

class FamilleProduitCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    code: str
    famille_parente_id: Optional[int | str] = None  # UUID or 0 for no parent

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
    nom: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    famille_parente_id: Optional[int | str] = None  # UUID or 0 for no parent

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
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[float] = 0
    famille_id: Optional[str] = None  # UUID
    has_stock: Optional[bool] = True  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = None  # ISO format date

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
    nom: Optional[str] = None
    description: Optional[str] = None
    prix_vente: Optional[float] = None
    seuil_stock_min: Optional[float] = None
    famille_id: Optional[str] = None  # UUID
    has_stock: Optional[bool] = None
    date_limite_consommation: Optional[str] = None

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
    produit_id: str  # UUID
    numero_lot: str
    quantite: int
    date_production: Optional[str] = None  # Format ISO
    date_peremption: Optional[str] = None  # Format ISO

class LotUpdate(BaseModel):
    quantite: Optional[int] = None
    date_peremption: Optional[str] = None  # Format ISO

class LotResponse(BaseModel):
    id: str  # UUID
    produit_id: str  # UUID
    numero_lot: str
    quantite: int
    date_production: Optional[str] = None  # Format ISO
    date_peremption: Optional[str] = None  # Format ISO

class FamilleProduitParent(BaseModel):
    id: str  # UUID
    nom: str
    description: Optional[str] = None
    code: str

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}

class FamilleProduitResponse(BaseModel):
    id: str  # UUID
    nom: str
    description: Optional[str] = None
    code: str
    famille_parente_id: Optional[str] = None  # UUID
    famille_parente: Optional[FamilleProduitParent] = None  # Informations de la famille parente

    @field_validator('id', 'famille_parente_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}

class ProduitResponse(BaseModel):
    id: str  # UUID
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[float] = 0
    cout_moyen: Optional[float] = 0
    famille_id: Optional[str] = None  # UUID
    station_id: Optional[str] = None  # UUID
    has_stock: Optional[bool] = True  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = None  # ISO format date

    @field_validator('id', 'famille_id', 'station_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}


class ProduitStockResponse(BaseModel):
    id: str  # UUID
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[float] = 0
    cout_moyen: Optional[float] = 0
    famille_id: Optional[str] = None  # UUID
    station_id: Optional[str] = None  # UUID
    has_stock: Optional[bool] = True  # True for products with stock, False for services
    date_limite_consommation: Optional[str] = None  # ISO format date
    quantite_stock: Optional[float] = 0  # Quantité disponible en stock

    @field_validator('id', 'famille_id', 'station_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = {'from_attributes': True}