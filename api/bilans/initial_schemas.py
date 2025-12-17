from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime, date
import uuid


class BilanInitialItem(BaseModel):
    """Modèle pour un élément du bilan initial"""
    type: str  # trésorerie, immobilisation, stock_carburant, stock_boutique, dette_creance
    libelle: str
    valeur: float
    devise: str = "XOF"
    details: Optional[Dict] = None

    @validator('type')
    def validate_type(cls, v):
        allowed_types = [
            'trésorerie', 'immobilisation', 'stock_carburant',
            'stock_boutique', 'dette_creance', 'autre'
        ]
        if v not in allowed_types:
            raise ValueError(f'Le type doit être un parmi: {", ".join(allowed_types)}')
        return v

    @validator('valeur')
    def validate_valeur(cls, v):
        if v < 0:
            raise ValueError('La valeur ne peut pas être négative')
        return v


class BilanInitialResponse(BaseModel):
    """Modèle de réponse pour le bilan initial"""
    date_bilan: datetime
    station_id: uuid.UUID
    actif_immobilise: float
    actif_circulant: float
    total_actif: float
    capitaux_propres: float
    dettes: float
    provisions: float
    total_passif: float
    details: Optional[Dict] = None


class BilanInitialCreateRequest(BaseModel):
    """Modèle pour la requête de création d'un bilan initial"""
    station_id: uuid.UUID


class BilanInitialCreate(BaseModel):
    """Modèle pour créer un bilan initial de départ dans la base de données"""
    compagnie_id: uuid.UUID
    station_id: Optional[uuid.UUID] = None
    date_bilan: date
    actif_immobilise: float
    actif_circulant: float
    capitaux_propres: float
    dettes: float
    provisions: float

    @validator('actif_immobilise', 'actif_circulant', 'capitaux_propres', 'dettes', 'provisions')
    def validate_non_negative_values(cls, v):
        if v < 0:
            raise ValueError('Les valeurs du bilan ne peuvent pas être négatives')
        return v


class BilanInitialUpdate(BaseModel):
    """Modèle pour mettre à jour un bilan initial de départ"""
    actif_immobilise: Optional[float] = None
    actif_circulant: Optional[float] = None
    capitaux_propres: Optional[float] = None
    dettes: Optional[float] = None
    provisions: Optional[float] = None


class BilanInitialDBResponse(BilanInitialCreate):
    """Modèle de réponse pour le bilan initial stocké dans la base de données"""
    id: uuid.UUID
    total_actif: float
    total_passif: float
    utilisateur_generation_id: uuid.UUID
    date_generation: datetime
    est_valide: bool