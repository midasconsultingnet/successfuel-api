from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Schema pour l'utilisateur
class UserCreate(BaseModel):
    nom: str = Field(..., description="Nom de l'utilisateur", example="Sall")
    prenom: str = Field(..., description="Prénom de l'utilisateur", example="Ahmadou")
    email: str = Field(..., description="Adresse email de l'utilisateur", example="a.sall@exemple.com")
    login: str = Field(..., description="Nom d'utilisateur pour la connexion", example="ahmadou_sall")
    password: str = Field(..., description="Mot de passe de l'utilisateur", example="motdepassetressecurise123")
    role: str = Field(..., description="Rôle de l'utilisateur", example="utilisateur_compagnie",
                     pattern="^(gerant_compagnie|utilisateur_compagnie)$")
    compagnie_id: str = Field(..., description="UUID de la compagnie", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")


class UserUpdate(BaseModel):
    nom: Optional[str] = Field(None, description="Nom de l'utilisateur", example="Sall")
    prenom: Optional[str] = Field(None, description="Prénom de l'utilisateur", example="Ahmadou")
    email: Optional[str] = Field(None, description="Adresse email de l'utilisateur", example="a.sall@exemple.com")
    login: Optional[str] = Field(None, description="Nom d'utilisateur pour la connexion", example="ahmadou_sall")
    password: Optional[str] = Field(None, description="Mot de passe de l'utilisateur", example="motdepassetressecurise123")
    role: Optional[str] = Field(None, description="Rôle de l'utilisateur", example="utilisateur_compagnie")
    actif: Optional[bool] = Field(None, description="Statut actif/inactif de l'utilisateur", example=True)


class UserResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de l'utilisateur", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    nom: str = Field(..., description="Nom de l'utilisateur", example="Sall")
    prenom: str = Field(..., description="Prénom de l'utilisateur", example="Ahmadou")
    email: str = Field(..., description="Adresse email de l'utilisateur", example="a.sall@exemple.com")
    login: str = Field(..., description="Nom d'utilisateur pour la connexion", example="ahmadou_sall")
    role: str = Field(..., description="Rôle de l'utilisateur", example="utilisateur_compagnie")
    created_at: datetime = Field(..., description="Date de création de l'utilisateur", example="2023-01-01T12:00:00")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière mise à jour", example="2023-01-02T14:30:00")
    date_derniere_connexion: Optional[datetime] = Field(None, description="Date de dernière connexion", example="2023-01-02T10:15:00")
    actif: bool = Field(..., description="Statut de l'utilisateur", example=True)
    compagnie_id: uuid.UUID = Field(..., description="Identifiant de la compagnie", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")

    class Config:
        from_attributes = True


# Schema pour la connexion
class UserLogin(BaseModel):
    login: str = Field(..., description="Nom d'utilisateur", example="ahmadou_sall")
    password: str = Field(..., description="Mot de passe", example="motdepassetressecurise123")


# Schema pour le token
class Token(BaseModel):
    access_token: str = Field(..., description="Token d'accès JWT", example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
    token_type: str = Field(..., description="Type de token", example="bearer")
    refresh_token: str = Field(..., description="Token de rafraîchissement", example="def50200d55e3e4...")


# Schema pour le token (sans refresh_token pour les réponses via cookie)
class TokenWithoutRefresh(BaseModel):
    access_token: str = Field(..., description="Token d'accès JWT", example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
    token_type: str = Field(..., description="Type de token", example="bearer")


class TokenData(BaseModel):
    login: Optional[str] = Field(None, description="Nom d'utilisateur du token", example="ahmadou_sall")


# Schema pour l'affectation utilisateur-station
class AffectationUtilisateurStationCreate(BaseModel):
    utilisateur_id: uuid.UUID = Field(..., description="UUID de l'utilisateur", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: str = Field(..., description="UUID de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")  # UUID de la station


class AffectationUtilisateurStationResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant de l'affectation", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    utilisateur_id: uuid.UUID = Field(..., description="UUID de l'utilisateur affecté", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    station_id: str = Field(..., description="UUID de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    date_affectation: datetime = Field(..., description="Date de l'affectation", example="2023-01-01T12:00:00")

    class Config:
        from_attributes = True


# Schema pour le token de session
class TokenSessionCreate(BaseModel):
    utilisateur_id: uuid.UUID = Field(..., description="UUID de l'utilisateur", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    token: str = Field(..., description="Token d'accès", example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
    token_refresh: str = Field(..., description="Token de rafraîchissement", example="def50200d55e3e4...")
    date_expiration: datetime = Field(..., description="Date d'expiration du token", example="2023-01-01T13:00:00")


class TokenSessionResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant du token de session", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    utilisateur_id: uuid.UUID = Field(..., description="UUID de l'utilisateur", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    token: str = Field(..., description="Token d'accès", example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
    date_expiration: datetime = Field(..., description="Date d'expiration du token", example="2023-01-01T13:00:00")
    actif: bool = Field(..., description="Statut actif/inactif du token", example=True)

    class Config:
        from_attributes = True


# Schema pour le journal d'actions
class JournalActionUtilisateurCreate(BaseModel):
    utilisateur_id: uuid.UUID = Field(..., description="UUID de l'utilisateur", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    type_action: str = Field(..., description="Type d'action effectuée (create, update, delete, read)", example="create",
                            pattern="^(create|update|delete|read)$")
    module_concerne: str = Field(..., description="Module concerné par l'action", example="user_management")
    donnees_avant: Optional[Dict[str, Any]] = Field(None, description="Données avant modification (pour update/delete)", example={"nom": "Sall", "prenom": "Ahmadou"})
    donnees_apres: Optional[Dict[str, Any]] = Field(None, description="Données après modification (pour create/update)", example={"nom": "Sall", "prenom": "Ahmadou", "email": "a.sall@exemple.com"})
    ip_utilisateur: Optional[str] = Field(None, description="Adresse IP de l'utilisateur", example="192.168.1.1")
    user_agent: Optional[str] = Field(None, description="User-Agent du navigateur ou application", example="Mozilla/5.0...")


class JournalActionUtilisateurResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant de l'action", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    utilisateur_id: uuid.UUID = Field(..., description="UUID de l'utilisateur", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    date_action: datetime = Field(..., description="Date de l'action", example="2023-01-01T12:00:00")
    type_action: str = Field(..., description="Type d'action effectuée", example="create")
    module_concerne: str = Field(..., description="Module concerné par l'action", example="user_management")
    donnees_avant: Optional[Dict[str, Any]] = Field(None, description="Données avant modification", example={"nom": "Sall", "prenom": "Ahmadou"})
    donnees_apres: Optional[Dict[str, Any]] = Field(None, description="Données après modification", example={"nom": "Sall", "prenom": "Ahmadou", "email": "a.sall@exemple.com"})
    ip_utilisateur: Optional[str] = Field(None, description="Adresse IP de l'utilisateur", example="192.168.1.1")
    user_agent: Optional[str] = Field(None, description="User-Agent du navigateur ou application", example="Mozilla/5.0...")

    class Config:
        from_attributes = True


# Schema pour la requête de refresh token
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Token de rafraîchissement", example="def50200d55e3e4...")


# Schema for station
class StationResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Identifiant unique de la station", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    compagnie_id: uuid.UUID = Field(..., description="Identifiant de la compagnie", example="3fa85f64-5717-4562-b3fc-2c963f66afa7")
    nom: str = Field(..., description="Nom de la station", example="Station Centre")
    code: str = Field(..., description="Code de la station", example="ST001")
    adresse: Optional[str] = Field(None, description="Adresse de la station", example="123 Avenue du Commerce, Dakar")
    statut: str = Field(..., description="Statut de la station", example="actif", pattern="^(actif|inactif|supprimer)$")
    date_creation: datetime = Field(..., description="Date de création de la station", example="2023-01-01T12:00:00")
    date_modification: Optional[datetime] = Field(None, description="Date de modification de la station", example="2023-01-02T14:30:00")
    est_actif: bool = Field(..., description="Statut actif/inactif de la station", example=True)

    class Config:
        from_attributes = True


# Schema for user with permissions
class UserWithPermissions(UserResponse):
    modules_autorises: List[str] = Field(default=[], description="Liste des modules autorisés", example=["Module Tiers", "Module Ventes", "Module Stocks"])
    station_affectee: Optional[StationResponse] = Field(None, description="Station affectée à l'utilisateur")
    stations_accessibles: List[StationResponse] = Field(default=[], description="Liste des stations accessibles pour les gérants de compagnie")