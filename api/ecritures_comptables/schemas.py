from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class EcritureComptableCreate(BaseModel):
    date_ecriture: datetime
    libelle_ecriture: str
    compte_debit: str  # UUID
    compte_credit: str  # UUID
    montant: float
    devise: Optional[str] = "XOF"
    tiers_id: Optional[str] = None  # UUID
    module_origine: Optional[str] = None  # Ex. : ventes, achats, charges
    reference_origine: Optional[str] = None  # Ex. : VTE-123
    est_validee: Optional[bool] = False

class EcritureComptableResponse(BaseModel):
    id: UUID
    date_ecriture: datetime
    libelle_ecriture: str
    compte_debit: str  # UUID
    compte_credit: str  # UUID
    montant: float
    devise: str
    tiers_id: Optional[str] = None  # UUID
    module_origine: Optional[str] = None
    reference_origine: Optional[str] = None
    utilisateur_id: Optional[str] = None  # UUID
    compagnie_id: str  # UUID
    est_validee: bool
    est_actif: bool
    created_at: datetime
    updated_at: datetime

class EcritureComptableUpdate(BaseModel):
    libelle_ecriture: Optional[str] = None
    montant: Optional[float] = None
    devise: Optional[str] = None
    tiers_id: Optional[str] = None  # UUID
    module_origine: Optional[str] = None
    reference_origine: Optional[str] = None

class GrandLivreItem(BaseModel):
    ecriture_id: UUID
    date_ecriture: datetime
    libelle_ecriture: str
    compte_id: UUID
    numero_compte: str
    intitule_compte: str
    tiers_id: Optional[UUID] = None
    module_origine: Optional[str] = None
    reference_origine: Optional[str] = None
    debit: float
    credit: float
    solde_cumule: float

class GrandLivreResponse(BaseModel):
    date_debut: datetime
    date_fin: datetime
    items: list[GrandLivreItem]
    total_items: int

class CompteResultatItem(BaseModel):
    numero_compte: str
    intitule_compte: str
    total_mouvement: float
    categorie: str  # CHARGES ou PRODUITS

class CompteResultatResponse(BaseModel):
    date_debut: datetime
    date_fin: datetime
    items: list[CompteResultatItem]
    total_produits: float
    total_charges: float
    resultat_net: float