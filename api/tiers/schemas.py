from pydantic import BaseModel
from typing import Optional

class TiersCreate(BaseModel):
    nom: str
    type: str  # client, fournisseur, employe
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
    solde: Optional[float] = None