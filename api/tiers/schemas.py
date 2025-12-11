from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# Schémas génériques - gardés pour la compatibilité
class TiersBase(BaseModel):
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None

class TiersCreate(BaseModel):
    nom: str
    type: str  # client, fournisseur, employé
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    # Specific fields based on type
    seuil_credit: Optional[float] = 0  # For clients
    conditions_paiement: Optional[str] = None  # For clients
    categorie_client: Optional[str] = None  # For clients: particulier, professionnel, etc.
    conditions_livraison: Optional[str] = None  # For fournisseurs
    delai_paiement: Optional[int] = None  # For fournisseurs (in days)
    poste: Optional[str] = None  # For employes
    date_embauche: Optional[str] = None  # For employes (ISO format)
    compagnie_id: str  # UUID of the associated company

class TiersUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    seuil_credit: Optional[float] = None
    conditions_paiement: Optional[str] = None
    categorie_client: Optional[str] = None
    conditions_livraison: Optional[str] = None
    delai_paiement: Optional[int] = None
    poste: Optional[str] = None
    date_embauche: Optional[str] = None
    statut: Optional[bool] = None
    # Champ solde supprimé pour refléter la nouvelle structure

# Schémas spécifiques pour les clients
class ClientCreate(BaseModel):
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    seuil_credit: Optional[float] = 0
    conditions_paiement: Optional[str] = None
    categorie_client: Optional[str] = None  # particulier, professionnel, etc.

class ClientUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    seuil_credit: Optional[float] = None
    conditions_paiement: Optional[str] = None
    categorie_client: Optional[str] = None

class ClientResponse(BaseModel):
    id: uuid.UUID
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    seuil_credit: Optional[float] = 0
    conditions_paiement: Optional[str] = None
    categorie_client: Optional[str] = None
    solde_actuel: float  # Remplacement du champ solde par solde_actuel calculé
    statut: str  # 'actif', 'inactif', 'supprimé'
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schémas spécifiques pour les fournisseurs
class FournisseurCreate(BaseModel):
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    conditions_livraison: Optional[str] = None
    delai_paiement: Optional[int] = None  # in days

class FournisseurUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    conditions_livraison: Optional[str] = None
    delai_paiement: Optional[int] = None

class FournisseurResponse(BaseModel):
    id: uuid.UUID
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    conditions_livraison: Optional[str] = None
    delai_paiement: Optional[int] = None
    solde_actuel: float  # Remplacement du champ solde par solde_actuel calculé
    statut: str  # 'actif', 'inactif', 'supprimé'
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schémas spécifiques pour les employés
class EmployeCreate(BaseModel):
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    poste: Optional[str] = None
    date_embauche: Optional[str] = None  # ISO format

class EmployeUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    poste: Optional[str] = None
    date_embauche: Optional[str] = None  # ISO format
    statut: Optional[str] = None  # 'actif', 'inactif', 'supprimé'

class EmployeResponse(BaseModel):
    id: uuid.UUID
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    poste: Optional[str] = None
    date_embauche: Optional[datetime] = None
    statut: str  # 'actif', 'inactif', 'supprimé'
    solde_actuel: float  # Ajout du solde_actuel pour les employés
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True