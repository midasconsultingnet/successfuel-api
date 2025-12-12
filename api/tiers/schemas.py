from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class TiersBase(BaseModel):
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: Optional[str] = "actif"
    donnees_personnelles: Optional[Dict[str, Any]] = None
    station_ids: Optional[List[uuid.UUID]] = []  # IDs des stations associées
    metadonnees: Optional[Dict[str, Any]] = None


class TiersCreate(TiersBase):
    pass

# Schémas spécifiques pour la documentation Swagger
class ClientCreate(BaseModel):
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: Optional[str] = "actif"
    donnees_personnelles: Optional[Dict[str, Any]] = None
    station_ids: Optional[List[uuid.UUID]] = []  # IDs des stations associées
    metadonnees: Optional[Dict[str, Any]] = None

class FournisseurCreate(BaseModel):
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: Optional[str] = "actif"
    donnees_personnelles: Optional[Dict[str, Any]] = None
    station_ids: Optional[List[uuid.UUID]] = []  # IDs des stations associées
    metadonnees: Optional[Dict[str, Any]] = None

class EmployeCreate(BaseModel):
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: Optional[str] = "actif"
    donnees_personnelles: Optional[Dict[str, Any]] = None
    station_ids: Optional[List[uuid.UUID]] = []  # IDs des stations associées
    metadonnees: Optional[Dict[str, Any]] = None


class TiersUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: Optional[str] = None
    donnees_personnelles: Optional[Dict[str, Any]] = None
    station_ids: Optional[List[uuid.UUID]] = None
    metadonnees: Optional[Dict[str, Any]] = None


class TiersResponse(TiersBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True