from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class BilanOperationnel(BaseModel):
    date_debut: datetime
    date_fin: datetime
    total_ventes: float
    total_achats: float
    resultat: float
    details: Optional[dict] = None  # Additional details in JSON format

class BilanTresorerie(BaseModel):
    date_debut: datetime
    date_fin: datetime
    solde_initial: float
    solde_final: float
    total_entrees: float
    total_sorties: float
    details: Optional[dict] = None  # Additional details in JSON format

class BilanStocks(BaseModel):
    date: datetime
    details: dict  # Details in JSON format
    # Example: {
    #   "carburant": {"essence": 10000, "diesel": 8000},
    #   "boutique": {"total_value": 500000},
    #   "gaz": {"total_value": 200000}
    # }

class BilanTiers(BaseModel):
    date: datetime
    type_tiers: str  # client, fournisseur, employe
    details: dict  # Details in JSON format

class GrandLivreItem(BaseModel):
    ecriture_id: uuid.UUID
    date_ecriture: datetime
    libelle_ecriture: str
    compte_id: uuid.UUID
    numero_compte: str
    intitule_compte: str
    tiers_id: Optional[uuid.UUID] = None
    module_origine: Optional[str] = None
    reference_origine: Optional[str] = None
    debit: float
    credit: float
    solde_cumule: float

class GrandLivreResponse(BaseModel):
    date_debut: datetime
    date_fin: datetime
    items: List[GrandLivreItem]
    total_items: int

class CompteResultatItem(BaseModel):
    numero_compte: str
    intitule_compte: str
    total_mouvement: float
    categorie: str  # CHARGES ou PRODUITS

class CompteResultatResponse(BaseModel):
    date_debut: datetime
    date_fin: datetime
    items: List[CompteResultatItem]
    total_produits: float
    total_charges: float
    resultat_net: float


class JournalOperationsItem(BaseModel):
    ecriture_id: uuid.UUID
    date_ecriture: datetime
    libelle_ecriture: str
    montant: float
    devise: str
    module_origine: str
    reference_origine: str
    tiers_nom: Optional[str] = None
    numero_compte: str
    intitule_compte: str


class JournalOperationsResponse(BaseModel):
    date_debut: datetime
    date_fin: datetime
    operations: List[JournalOperationsItem]
    total_operations: int


class JournalComptableItem(BaseModel):
    ecriture_id: uuid.UUID
    date_ecriture: datetime
    libelle_ecriture: str
    numero_compte: str
    intitule_compte: str
    debit: float
    credit: float


class JournalComptableResponse(BaseModel):
    date_debut: datetime
    date_fin: datetime
    ecritures: List[JournalComptableItem]
    total_ecritures: int