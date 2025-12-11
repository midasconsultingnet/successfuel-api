from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# Schema pour l'utilisateur
class UserCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    login: str
    password: str
    role: str  # gerant_compagnie, utilisateur_compagnie
    compagnie_id: str  # UUID de la compagnie


class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    actif: Optional[bool] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    nom: str
    prenom: str
    email: str
    login: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    date_derniere_connexion: Optional[datetime] = None
    actif: bool
    compagnie_id: uuid.UUID

    class Config:
        from_attributes = True


# Schema pour la connexion
class UserLogin(BaseModel):
    login: str
    password: str


# Schema pour le token
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


# Schema pour le token (sans refresh_token pour les réponses via cookie)
class TokenWithoutRefresh(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: Optional[str] = None


# Schema pour l'affectation utilisateur-station
class AffectationUtilisateurStationCreate(BaseModel):
    utilisateur_id: uuid.UUID
    station_id: str  # UUID de la station


class AffectationUtilisateurStationResponse(BaseModel):
    id: uuid.UUID
    utilisateur_id: uuid.UUID
    station_id: str
    date_affectation: datetime

    class Config:
        from_attributes = True


# Schema pour le token de session
class TokenSessionCreate(BaseModel):
    utilisateur_id: uuid.UUID
    token: str
    token_refresh: str
    date_expiration: datetime


class TokenSessionResponse(BaseModel):
    id: uuid.UUID
    utilisateur_id: uuid.UUID
    token: str
    date_expiration: datetime
    actif: bool

    class Config:
        from_attributes = True


# Schema pour le journal d'actions
class JournalActionUtilisateurCreate(BaseModel):
    utilisateur_id: uuid.UUID
    type_action: str  # create, update, delete, read
    module_concerne: str
    donnees_avant: Optional[dict] = None
    donnees_apres: Optional[dict] = None
    ip_utilisateur: Optional[str] = None
    user_agent: Optional[str] = None


class JournalActionUtilisateurResponse(BaseModel):
    id: uuid.UUID
    utilisateur_id: uuid.UUID
    date_action: datetime
    type_action: str
    module_concerne: str
    donnees_avant: Optional[dict] = None
    donnees_apres: Optional[dict] = None
    ip_utilisateur: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


# Schema pour la requête de refresh token
class RefreshTokenRequest(BaseModel):
    refresh_token: str