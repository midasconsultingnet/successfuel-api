from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class TiersBase(BaseModel):
    nom: str = Field(..., description="Nom du tiers", example="SARL Distributeur")
    email: Optional[str] = Field(None, description="Adresse email du tiers", example="contact@sarl-distributeur.sn")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone du tiers", example="+221338000000")
    adresse: Optional[str] = Field(None, description="Adresse du tiers", example="123 Avenue des Champs, Dakar")
    statut: Optional[str] = Field("actif", description="Statut du tiers", example="actif", pattern="^(actif|inactif|supprimé)$")
    donnees_personnelles: Optional[Dict[str, Any]] = Field(None, description="Données personnelles du tiers", example={"date_naissance": "1980-05-15", "ville_origine": "Dakar"})
    station_ids: Optional[List[uuid.UUID]] = Field([], description="IDs des stations associées", example=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    metadonnees: Optional[Dict[str, Any]] = Field(None, description="Métadonnées additionnelles", example={"source": "site_web", "note_interne": "Client prioritaire"})


class TiersCreate(TiersBase):
    pass

# Schémas spécifiques pour la documentation Swagger
class ClientCreate(BaseModel):
    nom: str = Field(..., description="Nom du client", example="SARL Distributeur")
    email: Optional[str] = Field(None, description="Adresse email du client", example="contact@sarl-distributeur.sn")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone du client", example="+221338000000")
    adresse: Optional[str] = Field(None, description="Adresse du client", example="123 Avenue des Champs, Dakar")
    statut: Optional[str] = Field("actif", description="Statut du client", example="actif", pattern="^(actif|inactif|supprimé)$")
    donnees_personnelles: Optional[Dict[str, Any]] = Field(None, description="Données personnelles du client", example={"date_naissance": "1980-05-15", "ville_origine": "Dakar"})
    station_ids: Optional[List[uuid.UUID]] = Field([], description="IDs des stations associées", example=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    metadonnees: Optional[Dict[str, Any]] = Field(None, description="Métadonnées additionnelles", example={"source": "site_web", "note_interne": "Client prioritaire"})

class FournisseurCreate(BaseModel):
    nom: str = Field(..., description="Nom du fournisseur", example="SARL Fournisseur")
    email: Optional[str] = Field(None, description="Adresse email du fournisseur", example="contact@sarl-fournisseur.sn")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone du fournisseur", example="+221338000000")
    adresse: Optional[str] = Field(None, description="Adresse du fournisseur", example="123 Avenue des Fournisseurs, Dakar")
    statut: Optional[str] = Field("actif", description="Statut du fournisseur", example="actif", pattern="^(actif|inactif|supprimé)$")
    donnees_personnelles: Optional[Dict[str, Any]] = Field(None, description="Données personnelles du fournisseur", example={"date_naissance": "1980-05-15", "ville_origine": "Dakar"})
    station_ids: Optional[List[uuid.UUID]] = Field([], description="IDs des stations associées", example=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    metadonnees: Optional[Dict[str, Any]] = Field(None, description="Métadonnées additionnelles", example={"source": "site_web", "note_interne": "Fournisseur prioritaire"})

class EmployeCreate(BaseModel):
    nom: str = Field(..., description="Nom de l'employé", example="Sall")
    prenom: Optional[str] = Field(None, description="Prénom de l'employé", example="Ahmadou")
    email: Optional[str] = Field(None, description="Adresse email de l'employé", example="a.sall@sarl-distributeur.sn")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone de l'employé", example="+221338000000")
    adresse: Optional[str] = Field(None, description="Adresse de l'employé", example="123 Avenue des Employés, Dakar")
    statut: Optional[str] = Field("actif", description="Statut de l'employé", example="actif", pattern="^(actif|inactif|supprimé)$")
    donnees_personnelles: Optional[Dict[str, Any]] = Field(None, description="Données personnelles de l'employé", example={"date_naissance": "1980-05-15", "ville_origine": "Dakar"})
    station_ids: Optional[List[uuid.UUID]] = Field([], description="IDs des stations associées", example=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    metadonnees: Optional[Dict[str, Any]] = Field(None, description="Métadonnées additionnelles", example={"date_embauche": "2023-01-15", "poste": "caissier"})

class TiersUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom du tiers", example="SARL Distributeur")
    email: Optional[str] = Field(None, description="Adresse email du tiers", example="contact@sarl-distributeur.sn")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone du tiers", example="+221338000000")
    adresse: Optional[str] = Field(None, description="Adresse du tiers", example="123 Avenue des Champs, Dakar")
    statut: Optional[str] = Field(None, description="Statut du tiers", example="actif")
    donnees_personnelles: Optional[Dict[str, Any]] = Field(None, description="Données personnelles du tiers", example={"date_naissance": "1980-05-15", "ville_origine": "Dakar"})
    station_ids: Optional[List[uuid.UUID]] = Field(None, description="IDs des stations associées", example=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    metadonnees: Optional[Dict[str, Any]] = Field(None, description="Métadonnées additionnelles", example={"source": "site_web", "note_interne": "Client prioritaire"})


class TiersResponse(TiersBase):
    id: uuid.UUID = Field(..., description="Identifiant unique du tiers", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    created_at: datetime = Field(..., description="Date de création du tiers", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")

    class Config:
        from_attributes = True