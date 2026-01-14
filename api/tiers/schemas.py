from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class TypeTiers(str, Enum):
    client = "client"
    fournisseur = "fournisseur"
    employe = "employé"


class StatutTiers(str, Enum):
    actif = "actif"
    inactif = "inactif"
    supprime = "supprimé"


class TiersBase(BaseModel):
    compagnie_id: UUID
    type: TypeTiers
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: StatutTiers = StatutTiers.actif
    donnees_personnelles: Optional[dict] = {}
    station_ids: Optional[List[str]] = []
    metadonnees: Optional[dict] = {}

    class Config:
        from_attributes = True


class TiersCreate(TiersBase):
    pass


class TiersUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: Optional[StatutTiers] = None
    compte_associe: Optional[UUID] = None
    donnees_personnelles: Optional[dict] = None
    station_ids: Optional[List[str]] = None
    metadonnees: Optional[dict] = None

    class Config:
        from_attributes = True


class TiersResponse(TiersBase):
    id: UUID
    date_creation: Optional[datetime] = None
    date_modification: Optional[datetime] = None

    class Config:
        from_attributes = True


class TiersCreateRequest(BaseModel):
    type: TypeTiers
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    statut: StatutTiers = StatutTiers.actif
    donnees_personnelles: Optional[dict] = {}
    station_ids: Optional[List[str]] = []
    metadonnees: Optional[dict] = {}

    class Config:
        from_attributes = True


class ClientCreateRequest(TiersCreateRequest):
    type: TypeTiers = TypeTiers.client  # Forcer le type à être client


class FournisseurCreateRequest(TiersCreateRequest):
    type: TypeTiers = TypeTiers.fournisseur  # Forcer le type à être fournisseur
    type_paiement: Optional[str] = None
    delai_paiement: Optional[str] = None
    acompte_requis: Optional[float] = None
    seuil_credit: Optional[float] = None


class EmployeCreateRequest(TiersCreateRequest):
    type: TypeTiers = TypeTiers.employe  # Forcer le type à être employé


class ClientCreate(TiersBase):
    type: TypeTiers = TypeTiers.client  # Forcer le type à être client


class FournisseurCreate(TiersBase):
    type: TypeTiers = TypeTiers.fournisseur  # Forcer le type à être fournisseur
    type_paiement: Optional[str] = None
    delai_paiement: Optional[str] = None
    acompte_requis: Optional[float] = None
    seuil_credit: Optional[float] = None


class EmployeCreate(TiersBase):
    type: TypeTiers = TypeTiers.employe  # Forcer le type à être employé


class SoldeTiersResponse(BaseModel):
    id: UUID
    tiers_id: UUID
    station_id: UUID
    montant_initial: float
    montant_actuel: float
    devise: str
    date_derniere_mise_a_jour: Optional[datetime] = None

    class Config:
        from_attributes = True