from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# Schémas pour le module Profils
class ProfilBase(BaseModel):
    nom: str = Field(..., max_length=255)
    description: Optional[str] = None
    compagnie_id: uuid.UUID  # Doit correspondre à une compagnie existante

class ProfilCreate(ProfilBase):
    pass

class ProfilUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None

class Profil(ProfilBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schémas pour le module Profil-Module
class ProfilModuleBase(BaseModel):
    profil_id: uuid.UUID
    module_nom: str = Field(
        ..., 
        description="Nom du module parmi la liste prédéfinie",
        examples=[
            "Module Utilisateurs et Authentification",
            "Module Structure de la Compagnie",
            "Module Tiers",
            "Module Produits et Stocks Complet",
            "Module tresoreries",
            "Module Achats Carburant",
            "Module Achats Boutique",
            "Module Ventes Carburant",
            "Module Ventes Boutique",
            "Module Livraisons Carburant",
            "Module Inventaires Carburant",
            "Module Inventaires Boutique",
            "Module Mouvements Financiers",
            "Module Salaires et Rémunérations",
            "Module Charges de Fonctionnement",
            "Module Immobilisations",
            "Module États, Bilans et Comptabilité"
        ]
    )

class ProfilModuleCreate(ProfilModuleBase):
    pass

class ProfilModule(ProfilModuleBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Schémas pour le module Utilisateur-Profils
class UtilisateurProfilBase(BaseModel):
    utilisateur_id: uuid.UUID
    profil_id: uuid.UUID

class UtilisateurProfilCreate(UtilisateurProfilBase):
    pass

class UtilisateurProfil(UtilisateurProfilBase):
    id: uuid.UUID
    date_affectation: datetime
    utilisateur_affectation_id: uuid.UUID

    class Config:
        from_attributes = True

# Schéma pour la réponse contenant un profil avec ses modules
class ProfilWithModules(Profil):
    modules: List[ProfilModule] = []

# Schéma pour la réponse contenant un utilisateur avec son profil
class UtilisateurWithProfil(BaseModel):
    id: uuid.UUID
    nom: str
    prenom: str
    email: str
    role: str
    profil: Optional[Profil] = None

    class Config:
        from_attributes = True