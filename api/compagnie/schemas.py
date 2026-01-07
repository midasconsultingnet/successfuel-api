from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Union, List
from decimal import Decimal
from datetime import datetime
import uuid

class CompagnieCreate(BaseModel):
    nom: str = Field(..., description="Nom de la compagnie", example="Succès Fuel SARL")
    pays_id: uuid.UUID = Field(..., description="ID du pays de la compagnie", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    adresse: Optional[str] = Field(None, description="Adresse de la compagnie", example="123 Avenue des Champs, Dakar")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone de la compagnie", example="+221338000000")
    email: Optional[str] = Field(None, description="Adresse email de la compagnie", example="contact@succesfuel.sn")
    devise: Optional[str] = Field("XOF", description="Devise utilisée par la compagnie", example="XOF")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"siret": "12345678901234", "rcs": "456789 Paris"})

    class Config:
        from_attributes = True

class CompagnieResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la compagnie", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    nom: str = Field(..., description="Nom de la compagnie", example="Succès Fuel SARL")
    pays_id: uuid.UUID = Field(..., description="ID du pays de la compagnie", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    adresse: Optional[str] = Field(None, description="Adresse de la compagnie", example="123 Avenue des Champs, Dakar")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone de la compagnie", example="+221338000000")
    email: Optional[str] = Field(None, description="Adresse email de la compagnie", example="contact@succesfuel.sn")
    devise: Optional[str] = Field("XOF", description="Devise utilisée par la compagnie", example="XOF")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"siret": "12345678901234", "rcs": "456789 Paris"})
    created_at: datetime = Field(..., description="Date de création de la compagnie", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True

class CompagnieUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom de la compagnie", example="Succès Fuel SARL")
    pays_id: Optional[uuid.UUID] = Field(None, description="ID du pays de la compagnie", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    adresse: Optional[str] = Field(None, description="Adresse de la compagnie", example="123 Avenue des Champs, Dakar")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone de la compagnie", example="+221338000000")
    email: Optional[str] = Field(None, description="Adresse email de la compagnie", example="contact@succesfuel.sn")
    devise: Optional[str] = Field(None, description="Devise utilisée par la compagnie", example="XOF")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"siret": "12345678901234", "rcs": "456789 Paris"})

    class Config:
        from_attributes = True

class StationCreate(BaseModel):
    nom: str = Field(..., description="Nom de la station", example="Station de la Gare")
    code: str = Field(..., description="Code unique de la station", example="ST-GARE-001")
    adresse: Optional[str] = Field(None, description="Adresse de la station", example="123 Avenue des Gares, Dakar")
    coordonnees_gps: Optional[Union[Dict[str, Any], str]] = Field(None, description="Coordonnées GPS de la station", example={"lat": 14.6937, "lng": -17.4440})
    groupe_id: Optional[uuid.UUID] = Field(None, description="ID du groupe partenaire", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"proprietaire": "M. Dupont", "date_construction": "2020-01-01"})

    @field_validator('coordonnees_gps', mode='before')
    @classmethod
    def validate_coordonnees_gps(cls, v):
        if v == "" or v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            if v == "":
                return None
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("coordonnees_gps must be a valid JSON string, dictionary, or empty string")
        return v

    class Config:
        from_attributes = True

class StationResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    compagnie_id: uuid.UUID = Field(..., description="ID de la compagnie associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    nom: str = Field(..., description="Nom de la station", example="Station de la Gare")
    code: str = Field(..., description="Code unique de la station", example="ST-GARE-001")
    adresse: Optional[str] = Field(None, description="Adresse de la station", example="123 Avenue des Gares, Dakar")
    coordonnees_gps: Optional[Dict[str, Any]] = Field(None, description="Coordonnées GPS de la station", example={"lat": 14.6937, "lng": -17.4440})
    statut: Optional[str] = Field("actif", description="Statut de la station", example="actif", pattern="^(actif|inactif|supprimer)$")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration JSON de la station", example={"completion": {"afficher_prix_unitaire": True}})
    groupe_id: Optional[uuid.UUID] = Field(None, description="ID du groupe partenaire", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"proprietaire": "M. Dupont", "date_construction": "2020-01-01"})
    created_at: datetime = Field(..., description="Date de création de la station", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True

class StationWithCompagnieResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    compagnie_id: uuid.UUID = Field(..., description="ID de la compagnie associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    compagnie: 'CompagnieResponse' = Field(..., description="Informations de la compagnie associée")
    nom: str = Field(..., description="Nom de la station", example="Station de la Gare")
    code: str = Field(..., description="Code unique de la station", example="ST-GARE-001")
    adresse: Optional[str] = Field(None, description="Adresse de la station", example="123 Avenue des Gares, Dakar")
    coordonnees_gps: Optional[Dict[str, Any]] = Field(None, description="Coordonnées GPS de la station", example={"lat": 14.6937, "lng": -17.4440})
    statut: Optional[str] = Field("actif", description="Statut de la station", example="actif", pattern="^(actif|inactif|supprimer)$")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration JSON de la station", example={"completion": {"afficher_prix_unitaire": True}})
    groupe_id: Optional[uuid.UUID] = Field(None, description="ID du groupe partenaire", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"proprietaire": "M. Dupont", "date_construction": "2020-01-01"})
    created_at: datetime = Field(..., description="Date de création de la station", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True


class StationUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom de la station", example="Station de la Gare")
    code: Optional[str] = Field(None, description="Code unique de la station", example="ST-GARE-001")
    adresse: Optional[str] = Field(None, description="Adresse de la station", example="123 Avenue des Gares, Dakar")
    coordonnees_gps: Optional[Union[Dict[str, Any], str]] = Field(None, description="Coordonnées GPS de la station", example={"lat": 14.6937, "lng": -17.4440})
    groupe_id: Optional[uuid.UUID] = Field(None, description="ID du groupe partenaire", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    infos_plus: Optional[Dict[str, Any]] = Field(None, description="Informations supplémentaires au format JSON", example={"proprietaire": "M. Dupont", "date_construction": "2020-01-01"})

    @field_validator('coordonnees_gps', mode='before')
    @classmethod
    def validate_coordonnees_gps(cls, v):
        if v == "" or v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            if v == "":
                return None
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("coordonnees_gps must be a valid JSON string, dictionary, or empty string")
        return v

    class Config:
        from_attributes = True

class CuveCreate(BaseModel):
    nom: str = Field(..., description="Nom de la cuve", example="Cuve principale A")
    code: str = Field(..., description="Code unique de la cuve", example="CP-A-001")
    capacite_maximale: int = Field(..., description="Capacité maximale de la cuve en litres", example=10000)
    carburant_id: uuid.UUID = Field(..., description="ID du type de carburant dans la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    statut: str = Field("actif", description="Statut de la cuve", example="actif", pattern="^(actif|inactif|maintenance)$")
    barremage: Optional[Union[str, List]] = Field(None, description="Barème de jaugeage de la cuve", example={"10": 1000, "20": 2000, "30": 3000})
    alert_stock: float = Field(0, description="Seuil d'alerte pour le stock", example=1000.0)

    class Config:
        from_attributes = True

class CarburantResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique du carburant", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    libelle: str = Field(..., description="Libellé du carburant", example="Essence Sans Plomb 95")
    code: str = Field(..., description="Code du carburant", example="ESP95")

    class Config:
        from_attributes = True


class PrixCarburantCreate(BaseModel):
    carburant_id: uuid.UUID = Field(..., description="ID du carburant", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: uuid.UUID = Field(..., description="ID de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    prix_achat: Optional[float] = Field(None, description="Prix d'achat du carburant", example=650.0)
    prix_vente: Optional[float] = Field(None, description="Prix de vente du carburant", example=680.0)


class PrixCarburantUpdate(BaseModel):
    prix_achat: Optional[float] = Field(None, description="Prix d'achat du carburant", example=650.0)
    prix_vente: Optional[float] = Field(None, description="Prix de vente du carburant", example=680.0)


class PrixCarburantResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique du prix", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    carburant_id: uuid.UUID = Field(..., description="ID du carburant", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: uuid.UUID = Field(..., description="ID de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    prix_achat: Optional[float] = Field(None, description="Prix d'achat du carburant", example=650.0)
    prix_vente: Optional[float] = Field(None, description="Prix de vente du carburant", example=680.0)
    created_at: datetime = Field(..., description="Date de création de l'enregistrement", example="2023-01-01T12:00:00")

    class Config:
        from_attributes = True


class PrixCarburantWithCarburantResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique du prix", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    carburant_id: uuid.UUID = Field(..., description="ID du carburant", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: uuid.UUID = Field(..., description="ID de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    prix_achat: Optional[float] = Field(None, description="Prix d'achat du carburant", example=650.0)
    prix_vente: Optional[float] = Field(None, description="Prix de vente du carburant", example=680.0)
    created_at: datetime = Field(..., description="Date de création de l'enregistrement", example="2023-01-01T12:00:00")
    # Informations du carburant
    carburant_libelle: str = Field(..., description="Libellé du carburant", example="Essence Sans Plomb 95")
    carburant_code: str = Field(..., description="Code du carburant", example="ESP95")

    class Config:
        from_attributes = True


class CuveResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: uuid.UUID = Field(..., description="ID de la station associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    nom: str = Field(..., description="Nom de la cuve", example="Cuve principale A")
    code: str = Field(..., description="Code unique de la cuve", example="CP-A-001")
    capacite_maximale: int = Field(..., description="Capacité maximale de la cuve en litres", example=10000)
    carburant_id: uuid.UUID = Field(..., description="ID du type de carburant dans la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    statut: str = Field("actif", description="Statut de la cuve", example="actif", pattern="^(actif|inactif|maintenance)$")
    barremage: Optional[Union[str, List]] = Field(None, description="Barème de jaugeage de la cuve", example={"10": 1000, "20": 2000, "30": 3000})
    alert_stock: float = Field(0, description="Seuil d'alerte pour le stock", example=1000.0)
    created_at: datetime = Field(..., description="Date de création de la cuve", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True


class StationForCuveResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    nom: str = Field(..., description="Nom de la station", example="Station de la Gare")
    code: str = Field(..., description="Code unique de la station", example="ST-GARE-001")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration JSON de la station", example={"completion": {"afficher_prix_unitaire": True}})

    class Config:
        from_attributes = True


class CuveWithCarburantResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: uuid.UUID = Field(..., description="ID de la station associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    nom: str = Field(..., description="Nom de la cuve", example="Cuve principale A")
    code: str = Field(..., description="Code unique de la cuve", example="CP-A-001")
    capacite_maximale: int = Field(..., description="Capacité maximale de la cuve en litres", example=10000)
    carburant_id: uuid.UUID = Field(..., description="ID du type de carburant dans la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    carburant: CarburantResponse = Field(..., description="Informations du carburant lié")
    statut: str = Field("actif", description="Statut de la cuve", example="actif", pattern="^(actif|inactif|maintenance)$")
    barremage: Optional[Union[str, List]] = Field(None, description="Barème de jaugeage de la cuve", example={"10": 1000, "20": 2000, "30": 3000})
    alert_stock: float = Field(0, description="Seuil d'alerte pour le stock", example=1000.0)
    created_at: datetime = Field(..., description="Date de création de la cuve", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True


class CuveWithStationResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: uuid.UUID = Field(..., description="ID de la station associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station: StationForCuveResponse = Field(..., description="Informations de la station associée")
    nom: str = Field(..., description="Nom de la cuve", example="Cuve principale A")
    code: str = Field(..., description="Code unique de la cuve", example="CP-A-001")
    capacite_maximale: int = Field(..., description="Capacité maximale de la cuve en litres", example=10000)
    carburant_id: uuid.UUID = Field(..., description="ID du type de carburant dans la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    statut: str = Field("actif", description="Statut de la cuve", example="actif", pattern="^(actif|inactif|maintenance)$")
    barremage: Optional[Union[str, List]] = Field(None, description="Barème de jaugeage de la cuve", example={"10": 1000, "20": 2000, "30": 3000})
    alert_stock: float = Field(0, description="Seuil d'alerte pour le stock", example=1000.0)
    created_at: datetime = Field(..., description="Date de création de la cuve", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True


class StockCuveResponse(BaseModel):
    cuve_id: uuid.UUID = Field(..., description="Identifiant unique de la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: uuid.UUID = Field(..., description="ID de la station associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    carburant_id: uuid.UUID = Field(..., description="ID du type de carburant", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    cuve_nom: str = Field(..., description="Nom de la cuve", example="Cuve principale A")
    cuve_code: str = Field(..., description="Code unique de la cuve", example="CP-A-001")
    capacite_maximale: int = Field(..., description="Capacité maximale de la cuve en litres", example=10000)
    cuve_statut: str = Field(..., description="Statut de la cuve", example="actif")
    alert_stock: float = Field(0, description="Seuil d'alerte pour le stock", example=1000.0)
    stock_initial: float = Field(..., description="Stock initial de la cuve", example=0.0)
    stock_actuel: float = Field(..., description="Stock actuel de la cuve", example=5000.0)
    derniere_date_mouvement: datetime = Field(..., description="Date du dernier mouvement de stock", example="2023-01-01T12:00:00")
    date_dernier_mouvement: Optional[datetime] = Field(None, description="Date du dernier mouvement de stock", example="2023-01-01T12:00:00")
    carburant_libelle: str = Field(..., description="Libellé du carburant", example="Essence Sans Plomb 95")
    carburant_code: str = Field(..., description="Code du carburant", example="ESP95")
    station_nom: str = Field(..., description="Nom de la station", example="Station de la Gare")
    station_code: str = Field(..., description="Code unique de la station", example="ST-GARE-001")
    compagnie_nom: str = Field(..., description="Nom de la compagnie", example="Succès Fuel SARL")

    class Config:
        from_attributes = True

class CuveUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom de la cuve", example="Cuve principale A")
    code: Optional[str] = Field(None, description="Code unique de la cuve", example="CP-A-001")
    capacite_maximale: Optional[int] = Field(None, description="Capacité maximale de la cuve en litres", example=10000)
    carburant_id: Optional[uuid.UUID] = Field(None, description="ID du type de carburant dans la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    statut: Optional[str] = Field(None, description="Statut de la cuve", example="actif")
    barremage: Optional[Union[str, List]] = Field(None, description="Barème de jaugeage de la cuve", example={"10": 1000, "20": 2000, "30": 3000})
    alert_stock: Optional[float] = Field(None, description="Seuil d'alerte pour le stock", example=1000.0)

    class Config:
        from_attributes = True

class PistoletCreate(BaseModel):
    numero: str = Field(..., description="Numéro unique du pistolet", example="P001")
    statut: str = Field("actif", description="Statut du pistolet", example="actif", pattern="^(actif|inactif|maintenance)$")
    index_initial: Union[float, Decimal] = Field(0.0, description="Index initial du pistolet", example=0.0)
    index_final: Optional[Union[float, Decimal]] = Field(None, description="Index final du pistolet", example=1000.0)
    date_derniere_utilisation: Optional[datetime] = Field(None, description="Date de dernière utilisation", example="2023-01-01T12:00:00")

    class Config:
        from_attributes = True

class PistoletResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique du pistolet", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    cuve_id: uuid.UUID = Field(..., description="ID de la cuve associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    numero: str = Field(..., description="Numéro unique du pistolet", example="P001")
    statut: str = Field("actif", description="Statut du pistolet", example="actif", pattern="^(actif|inactif|maintenance)$")
    index_initial: Union[float, Decimal] = Field(0.0, description="Index initial du pistolet", example=0.0)
    index_final: Optional[Union[float, Decimal]] = Field(None, description="Index final du pistolet", example=1000.0)
    date_derniere_utilisation: Optional[datetime] = Field(None, description="Date de dernière utilisation", example="2023-01-01T12:00:00")
    created_at: datetime = Field(..., description="Date de création du pistolet", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True

class CuveResponseForPistolet(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    nom: str = Field(..., description="Nom de la cuve", example="Cuve principale A")
    code: str = Field(..., description="Code unique de la cuve", example="CP-A-001")
    capacite_maximale: int = Field(..., description="Capacité maximale de la cuve en litres", example=10000)
    carburant_id: uuid.UUID = Field(..., description="ID du type de carburant dans la cuve", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    statut: str = Field("actif", description="Statut de la cuve", example="actif", pattern="^(actif|inactif|maintenance)$")
    alert_stock: float = Field(0, description="Seuil d'alerte pour le stock", example=1000.0)
    created_at: datetime = Field(..., description="Date de création de la cuve", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True


class PistoletWithCuveResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique du pistolet", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    cuve_id: uuid.UUID = Field(..., description="ID de la cuve associée", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    cuve: CuveResponseForPistolet = Field(..., description="Informations de la cuve associée")
    numero: str = Field(..., description="Numéro unique du pistolet", example="P001")
    statut: str = Field("actif", description="Statut du pistolet", example="actif", pattern="^(actif|inactif|maintenance)$")
    index_initial: Union[float, Decimal] = Field(0.0, description="Index initial du pistolet", example=0.0)
    index_final: Optional[Union[float, Decimal]] = Field(None, description="Index final du pistolet", example=1000.0)
    date_derniere_utilisation: Optional[datetime] = Field(None, description="Date de dernière utilisation", example="2023-01-01T12:00:00")
    created_at: datetime = Field(..., description="Date de création du pistolet", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True


class ProduitBoutiqueResponse(BaseModel):
    id: uuid.UUID
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[int] = 0
    famille_id: Optional[int] = None
    station_id: uuid.UUID  # Ajout de l'ID de la station
    has_stock: Optional[bool] = True  # True for products with stock, False for services
    date_limite_consommation: Optional[datetime] = None

    class Config:
        from_attributes = True


class StationForProduitBoutique(BaseModel):
    id: uuid.UUID
    nom: str
    code: str
    config: Optional[Dict[str, Any]] = None  # JSON configuration object

    class Config:
        from_attributes = True


class ProduitBoutiqueWithStationResponse(BaseModel):
    id: uuid.UUID
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[int] = 0
    famille_id: Optional[int] = None
    station_id: uuid.UUID
    station: StationForProduitBoutique  # Information de la station associée
    has_stock: Optional[bool] = True  # True for products with stock, False for services
    date_limite_consommation: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockProduitResponse(BaseModel):
    id: uuid.UUID
    produit_id: uuid.UUID
    station_id: uuid.UUID
    quantite_theorique: float = 0
    quantite_reelle: float = 0
    date_dernier_calcul: Optional[datetime] = None
    cout_moyen_pondere: float = 0

    class Config:
        from_attributes = True


class ProduitWithStockResponse(BaseModel):
    id: uuid.UUID
    nom: str
    code: str
    description: Optional[str] = None
    unite_mesure: Optional[str] = "unité"
    type: str  # boutique, lubrifiant, gaz, service
    prix_vente: float
    seuil_stock_min: Optional[int] = 0
    famille_id: Optional[int] = None
    station_id: uuid.UUID
    has_stock: Optional[bool] = True
    date_limite_consommation: Optional[datetime] = None
    stock: StockProduitResponse  # Stock associé au produit

    class Config:
        from_attributes = True


class PistoletUpdate(BaseModel):
    numero: Optional[str] = None
    statut: Optional[str] = None
    index_initial: Optional[Union[float, Decimal]] = None
    index_final: Optional[Union[float, Decimal]] = None
    date_derniere_utilisation: Optional[datetime] = None

    class Config:
        from_attributes = True

class EtatInitialCuveCreateForPath(BaseModel):
    hauteur_jauge_initiale: float = Field(
        ...,
        description="Hauteur de jauge initiale en centimètres",
        example=100.0
    )

    class Config:
        from_attributes = True


class EtatInitialCuveCreate(BaseModel):
    cuve_id: uuid.UUID = Field(
        ...,
        description="ID de la cuve",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6"
    )
    hauteur_jauge_initiale: float = Field(
        ...,
        description="Hauteur de jauge initiale en centimètres",
        example=100.0
    )
    volume_initial_calcule: Optional[float] = Field(
        default=None,
        description="Volume initial calculé. Si non fourni, sera automatiquement calculé à partir de la hauteur jauge et du barremage de la cuve.",
        example=1000.0
    )
    date_initialisation: datetime = Field(
        ...,
        description="Date et heure d'initialisation",
        example="2025-12-13T13:10:59.539Z"
    )
    utilisateur_id: uuid.UUID = Field(
        ...,
        description="ID de l'utilisateur effectuant l'initialisation",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6"
    )

    class Config:
        from_attributes = True

class CarburantResponse(BaseModel):
    id: uuid.UUID
    libelle: str
    code: str

    class Config:
        from_attributes = True


class CuveResponseForEtatInitial(BaseModel):
    id: uuid.UUID
    nom: str
    code: str
    capacite_maximale: int
    alert_stock: float = 0  # Seuil d'alerte pour le stock
    carburant: CarburantResponse  # Ajout des informations du carburant

    class Config:
        from_attributes = True


class EtatInitialCuveWithCuveCarburantResponse(BaseModel):
    id: uuid.UUID
    cuve_id: uuid.UUID
    cuve: CuveResponseForEtatInitial  # Ajout des informations de la cuve
    hauteur_jauge_initiale: float
    volume_initial_calcule: float
    date_initialisation: datetime
    utilisateur_id: uuid.UUID
    verrouille: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EtatInitialCuveResponse(BaseModel):
    id: uuid.UUID
    cuve_id: uuid.UUID
    hauteur_jauge_initiale: float
    volume_initial_calcule: float
    date_initialisation: datetime
    utilisateur_id: uuid.UUID
    verrouille: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EtatInitialCuveUpdate(BaseModel):
    hauteur_jauge_initiale: Optional[float] = None
    volume_initial_calcule: Optional[float] = None
    date_initialisation: Optional[datetime] = None
    verrouille: Optional[bool] = None

    class Config:
        from_attributes = True


class MouvementStockCuveCreate(BaseModel):
    # Les relations avec les tables d'origine sont optionnelles selon le type de mouvement
    livraison_carburant_id: Optional[uuid.UUID] = None
    vente_carburant_id: Optional[uuid.UUID] = None
    inventaire_carburant_id: Optional[uuid.UUID] = None
    cuve_id: uuid.UUID
    type_mouvement: str  # 'entrée', 'sortie', 'ajustement'
    quantite: float
    date_mouvement: datetime
    reference_origine: str
    module_origine: str
    utilisateur_id: uuid.UUID

    class Config:
        from_attributes = True


class MouvementStockCuveResponse(BaseModel):
    id: uuid.UUID
    livraison_carburant_id: Optional[uuid.UUID] = None
    vente_carburant_id: Optional[uuid.UUID] = None
    inventaire_carburant_id: Optional[uuid.UUID] = None
    cuve_id: uuid.UUID
    type_mouvement: str  # 'entrée', 'sortie', 'ajustement'
    quantite: float
    date_mouvement: datetime
    stock_avant: Optional[float] = None
    stock_apres: Optional[float] = None
    utilisateur_id: uuid.UUID
    reference_origine: str
    module_origine: str
    statut: str = "validé"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CuveForPistoletResponse(BaseModel):
    id: uuid.UUID
    nom: str
    code: str

    class Config:
        from_attributes = True


class PistoletWithCuveResponse(BaseModel):
    id: uuid.UUID
    cuve_id: uuid.UUID
    cuve: CuveForPistoletResponse  # Information de la cuve associée
    numero: str
    statut: str = "actif"
    index_initial: Union[float, Decimal] = 0.0
    index_final: Optional[Union[float, Decimal]] = None
    date_derniere_utilisation: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MouvementStockCuveUpdate(BaseModel):
    statut: Optional[str] = None  # 'validé', 'annulé'

    class Config:
        from_attributes = True


class PistoletWithCuveForStationResponse(BaseModel):
    id: uuid.UUID
    cuve_id: uuid.UUID
    cuve: CuveResponseForPistolet  # Information de la cuve associée
    numero: str
    statut: str = "actif"
    index_initial: Union[float, Decimal] = 0.0
    index_final: Optional[Union[float, Decimal]] = None
    date_derniere_utilisation: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StationConfigUpdate(BaseModel):
    completion: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True