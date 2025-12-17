from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Union
from datetime import datetime
import uuid

class CompagnieCreate(BaseModel):
    nom: str
    pays_id: uuid.UUID
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    devise: Optional[str] = "XOF"

    class Config:
        from_attributes = True

class CompagnieResponse(BaseModel):
    id: uuid.UUID
    nom: str
    pays_id: uuid.UUID
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    devise: Optional[str] = "XOF"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CompagnieUpdate(BaseModel):
    nom: Optional[str] = None
    pays_id: Optional[uuid.UUID] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    devise: Optional[str] = None

    class Config:
        from_attributes = True

class StationCreate(BaseModel):
    nom: str
    code: str
    adresse: Optional[str] = None
    coordonnees_gps: Optional[Union[Dict[str, Any], str]] = None

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
    id: uuid.UUID
    compagnie_id: uuid.UUID
    nom: str
    code: str
    adresse: Optional[str] = None
    coordonnees_gps: Optional[Dict[str, Any]] = None
    statut: Optional[str] = "actif"
    config: Optional[Dict[str, Any]] = None  # JSON configuration object
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CompagnieResponse(BaseModel):
    id: uuid.UUID
    nom: str
    pays_id: uuid.UUID
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    devise: Optional[str] = "XOF"

    class Config:
        from_attributes = True


class StationWithCompagnieResponse(BaseModel):
    id: uuid.UUID
    compagnie_id: uuid.UUID
    compagnie: 'CompagnieResponse'  # Information de la compagnie associée
    nom: str
    code: str
    adresse: Optional[str] = None
    coordonnees_gps: Optional[Dict[str, Any]] = None
    statut: Optional[str] = "actif"
    config: Optional[Dict[str, Any]] = None  # JSON configuration object
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StationUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    adresse: Optional[str] = None
    coordonnees_gps: Optional[Union[Dict[str, Any], str]] = None

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
    nom: str
    code: str
    capacite_maximale: int
    niveau_actuel: int = 0
    carburant_id: uuid.UUID
    statut: str = "actif"
    barremage: Optional[Union[str, list]] = None  # Facultatif à la création
    alert_stock: float = 0  # Seuil d'alerte pour le stock

    class Config:
        from_attributes = True

class CarburantResponse(BaseModel):
    id: uuid.UUID
    libelle: str
    code: str

    class Config:
        from_attributes = True


class PrixCarburantCreate(BaseModel):
    carburant_id: uuid.UUID
    station_id: uuid.UUID
    prix_achat: Optional[float] = None
    prix_vente: Optional[float] = None


class PrixCarburantUpdate(BaseModel):
    prix_achat: Optional[float] = None
    prix_vente: Optional[float] = None


class PrixCarburantResponse(BaseModel):
    id: uuid.UUID
    carburant_id: uuid.UUID
    station_id: uuid.UUID
    prix_achat: Optional[float] = None
    prix_vente: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PrixCarburantWithCarburantResponse(BaseModel):
    id: uuid.UUID
    carburant_id: uuid.UUID
    station_id: uuid.UUID
    prix_achat: Optional[float] = None
    prix_vente: Optional[float] = None
    created_at: datetime
    # Informations du carburant
    carburant_libelle: str
    carburant_code: str

    class Config:
        from_attributes = True


class CuveResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    nom: str
    code: str
    capacite_maximale: int
    niveau_actuel: int = 0
    carburant_id: uuid.UUID
    statut: str = "actif"
    barremage: Optional[Union[str, list]] = None
    alert_stock: float = 0  # Seuil d'alerte pour le stock
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StationForCuveResponse(BaseModel):
    id: uuid.UUID
    nom: str
    code: str
    config: Optional[Dict[str, Any]] = None  # JSON configuration object

    class Config:
        from_attributes = True


class CuveWithCarburantResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    nom: str
    code: str
    capacite_maximale: int
    niveau_actuel: int = 0
    carburant_id: uuid.UUID
    carburant: CarburantResponse  # Ajout du carburant lié
    statut: str = "actif"
    barremage: Optional[Union[str, list]] = None
    alert_stock: float = 0  # Seuil d'alerte pour le stock
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CuveWithStationResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    station: StationForCuveResponse  # Information de la station associée
    nom: str
    code: str
    capacite_maximale: int
    niveau_actuel: int = 0
    carburant_id: uuid.UUID
    statut: str = "actif"
    barremage: Optional[Union[str, list]] = None
    alert_stock: float = 0  # Seuil d'alerte pour le stock
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockCuveResponse(BaseModel):
    cuve_id: uuid.UUID
    station_id: uuid.UUID
    carburant_id: uuid.UUID
    cuve_nom: str
    cuve_code: str
    capacite_maximale: int
    cuve_statut: str
    alert_stock: float = 0  # Seuil d'alerte pour le stock
    stock_initial: float
    stock_actuel: float
    derniere_date_mouvement: datetime
    date_dernier_mouvement: Optional[datetime] = None
    carburant_libelle: str
    carburant_code: str
    station_nom: str
    station_code: str
    compagnie_nom: str

    class Config:
        from_attributes = True

class CuveUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    capacite_maximale: Optional[int] = None
    niveau_actuel: Optional[int] = None
    carburant_id: Optional[uuid.UUID] = None
    statut: Optional[str] = None
    barremage: Optional[Union[str, list]] = None  # Peut être mis à jour
    alert_stock: Optional[float] = None  # Seuil d'alerte pour le stock

    class Config:
        from_attributes = True

class PistoletCreate(BaseModel):
    numero: str
    statut: str = "actif"
    index_initial: int = 0
    index_final: Optional[int] = None
    date_derniere_utilisation: Optional[datetime] = None

    class Config:
        from_attributes = True

class PistoletResponse(BaseModel):
    id: uuid.UUID
    cuve_id: uuid.UUID
    numero: str
    statut: str = "actif"
    index_initial: int = 0
    index_final: Optional[int] = None
    date_derniere_utilisation: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CuveResponseForPistolet(BaseModel):
    id: uuid.UUID
    nom: str
    code: str
    capacite_maximale: int
    niveau_actuel: int = 0
    carburant_id: uuid.UUID
    statut: str = "actif"
    alert_stock: float = 0  # Seuil d'alerte pour le stock
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PistoletWithCuveResponse(BaseModel):
    id: uuid.UUID
    cuve_id: uuid.UUID
    cuve: CuveResponseForPistolet  # Information de la cuve associée
    numero: str
    statut: str = "actif"
    index_initial: int = 0
    index_final: Optional[int] = None
    date_derniere_utilisation: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    index_initial: Optional[int] = None
    index_final: Optional[int] = None
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
    index_initial: int = 0
    index_final: Optional[int] = None
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
    index_initial: int = 0
    index_final: Optional[int] = None
    date_derniere_utilisation: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StationConfigUpdate(BaseModel):
    completion: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True