from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

class PlanComptableBase(BaseModel):
    """Schéma de base pour le plan comptable"""
    numero_compte: Optional[str] = Field(None, max_length=50, description="Numéro unique du compte (optionnel, généré automatiquement si parent_id est spécifié)")
    libelle_compte: str = Field(..., max_length=255, description="Libellé du compte")
    categorie: Optional[str] = Field(None, max_length=100, description="Catégorie du compte (Actif, Passif, Produit, Charge) - optionnel si parent_id est spécifié")
    type_compte: Optional[str] = Field(None, max_length=50, description="Type de compte (Bilan, Resultat, etc.) - optionnel si parent_id est spécifié")
    parent_id: Optional[UUID] = Field(None, description="Identifiant du compte parent pour la hiérarchie")
    compagnie_id: Optional[UUID] = Field(None, description="Identifiant de la compagnie (pour les sous-comptes)")

class PlanComptableCreate(PlanComptableBase):
    """Schéma pour la création d'un compte dans le plan comptable"""
    pass

class PlanComptableUpdate(BaseModel):
    """Schéma pour la mise à jour d'un compte dans le plan comptable"""
    numero_compte: Optional[str] = Field(None, max_length=50)
    libelle_compte: Optional[str] = Field(None, max_length=255)
    categorie: Optional[str] = Field(None, max_length=100)
    type_compte: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[UUID] = None
    compagnie_id: Optional[UUID] = Field(None)

class PlanComptableResponse(PlanComptableBase):
    """Schéma pour la réponse contenant un compte du plan comptable"""
    id: UUID
    est_actif: bool

    class Config:
        from_attributes = True

class PlanComptableHierarchyResponse(PlanComptableResponse):
    """Schéma pour la réponse avec la hiérarchie du plan comptable"""
    enfants: List['PlanComptableHierarchyResponse'] = []

    class Config:
        from_attributes = True

# Pour résoudre l'erreur de référence circulaire
PlanComptableHierarchyResponse.update_forward_refs()