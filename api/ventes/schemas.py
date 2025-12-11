from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VenteDetailCreate(BaseModel):
    produit_id: str  # UUID
    quantite: int
    prix_unitaire: float
    montant: float
    remise: Optional[float] = 0

class VenteDetailUpdate(BaseModel):
    quantite: Optional[int] = None
    prix_unitaire: Optional[float] = None
    montant: Optional[float] = None
    remise: Optional[float] = None

class VenteCreate(BaseModel):
    client_id: Optional[str] = None  # UUID - Optional for cash sales
    date: datetime
    statut: str  # en_cours, terminee, annulee
    type_vente: str  # produit, service, hybride
    trésorerie_id: str  # UUID of the cash register used
    numero_piece_comptable: Optional[str] = None
    details: List[VenteDetailCreate]

class VenteUpdate(BaseModel):
    client_id: Optional[str] = None
    date: Optional[datetime] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None
    type_vente: Optional[str] = None
    trésorerie_id: Optional[str] = None
    numero_piece_comptable: Optional[str] = None

# Schémas pour les ventes de carburant
class VenteCarburantCreate(BaseModel):
    station_id: str  # UUID
    cuve_id: str  # UUID
    pistolet_id: str  # UUID
    quantite_vendue: float  # En litres
    prix_unitaire: float
    montant_total: float
    date_vente: datetime
    index_initial: float
    index_final: float
    pompiste: str  # Nom du pompiste
    qualite_marshalle_id: Optional[str] = None  # UUID du contrôleur qualité
    montant_paye: Optional[float] = 0
    mode_paiement: Optional[str] = None  # espèce, chèque, carte crédit, note de crédit, crédit client
    utilisateur_id: str  # UUID de l'utilisateur qui enregistre la vente

class VenteCarburantUpdate(BaseModel):
    montant_paye: Optional[float] = None
    mode_paiement: Optional[str] = None
    statut: Optional[str] = None  # enregistrée, validée, annulée
    numero_piece_comptable: Optional[str] = None

class CreanceEmployeCreate(BaseModel):
    vente_carburant_id: Optional[str] = None  # UUID
    pompiste: str  # Nom du pompiste
    montant_du: float
    montant_paye: Optional[float] = 0
    created_at: datetime
    date_echeance: Optional[datetime] = None
    utilisateur_gestion_id: str  # UUID

class CreanceEmployeUpdate(BaseModel):
    montant_paye: Optional[float] = None
    date_echeance: Optional[datetime] = None
    statut: Optional[str] = None  # en_cours, payé, partiellement_payé