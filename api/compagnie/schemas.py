from pydantic import BaseModel
from typing import Optional
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
    coordonnees_gps: Optional[str] = None
    statut: Optional[str] = "actif"

    class Config:
        from_attributes = True

class StationResponse(BaseModel):
    id: uuid.UUID
    compagnie_id: uuid.UUID
    nom: str
    code: str
    adresse: Optional[str] = None
    coordonnees_gps: Optional[str] = None
    statut: Optional[str] = "actif"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StationUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    adresse: Optional[str] = None
    coordonnees_gps: Optional[str] = None
    statut: Optional[str] = None

    class Config:
        from_attributes = True

class CuveCreate(BaseModel):
    station_id: Optional[uuid.UUID] = None
    nom: str
    code: str
    capacite_maximale: int
    niveau_actuel: int = 0
    carburant_id: uuid.UUID
    statut: str = "actif"
    barremage: Optional[str] = None  # Facultatif à la création

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
    barremage: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CuveUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    capacite_maximale: Optional[int] = None
    niveau_actuel: Optional[int] = None
    carburant_id: Optional[uuid.UUID] = None
    statut: Optional[str] = None
    barremage: Optional[str] = None  # Peut être mis à jour

    class Config:
        from_attributes = True

class PistoletCreate(BaseModel):
    cuve_id: uuid.UUID
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

class PistoletUpdate(BaseModel):
    numero: Optional[str] = None
    statut: Optional[str] = None
    index_initial: Optional[int] = None
    index_final: Optional[int] = None
    date_derniere_utilisation: Optional[datetime] = None

    class Config:
        from_attributes = True

class EtatInitialCuveCreate(BaseModel):
    cuve_id: uuid.UUID
    hauteur_jauge_initiale: float
    volume_initial_calcule: float
    date_initialisation: datetime
    utilisateur_id: uuid.UUID

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