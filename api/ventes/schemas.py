from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class VenteDetailCreate(BaseModel):
    produit_id: uuid.UUID  # UUID
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
    client_id: Optional[uuid.UUID] = None  # UUID - Optional for cash sales
    date: datetime
    statut: str  # en_cours, terminee, annulee
    type_vente: str  # produit, service, hybride
    trésorerie_station_id: uuid.UUID  # UUID of the cash register used (now referencing the new structure)
    numero_piece_comptable: Optional[str] = None
    details: List[VenteDetailCreate]

    class Config:
        from_attributes = True

class VenteUpdate(BaseModel):
    client_id: Optional[uuid.UUID] = None
    date: Optional[datetime] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None
    type_vente: Optional[str] = None
    trésorerie_station_id: Optional[uuid.UUID] = None
    numero_piece_comptable: Optional[str] = None

    class Config:
        from_attributes = True

# Schémas pour les ventes de carburant
class VenteCarburantCreate(BaseModel):
    station_id: uuid.UUID  # UUID
    cuve_id: uuid.UUID  # UUID
    pistolet_id: uuid.UUID  # UUID
    trésorerie_station_id: Optional[uuid.UUID] = None  # UUID - Ajouté pour la gestion des paiements par trésorerie
    carburant_id: Optional[uuid.UUID] = None  # UUID - Ajouté pour la gestion des prix de vente
    quantite_vendue: float  # En litres
    prix_unitaire: Optional[float] = None  # Le prix unitaire sera obtenu via la table prix_carburant
    montant_total: Optional[float] = None
    date_vente: datetime
    index_initial: float
    index_final: float
    quantite_mesuree: Optional[float] = None  # En litres - calculée à partir des index (index_final - index_initial)
    ecart_quantite: Optional[float] = None  # Différence entre quantite_vendue et quantite_mesuree
    besoin_compensation: Optional[bool] = False  # Indique si une compensation est nécessaire
    compensation_id: Optional[uuid.UUID] = None  # Référence à l'avoir de compensation si nécessaire
    pompiste: str  # Nom du pompiste
    qualite_marshalle_id: Optional[uuid.UUID] = None  # UUID du contrôleur qualité
    montant_paye: Optional[float] = 0
    mode_paiement: Optional[str] = None  # espèce, chèque, carte crédit, note de crédit, crédit client
    utilisateur_id: uuid.UUID  # UUID de l'utilisateur qui enregistre la vente

    class Config:
        from_attributes = True

class VenteCarburantUpdate(BaseModel):
    montant_paye: Optional[float] = None
    mode_paiement: Optional[str] = None
    statut: Optional[str] = None  # enregistrée, validée, annulée
    numero_piece_comptable: Optional[str] = None

    class Config:
        from_attributes = True

class CreanceEmployeCreate(BaseModel):
    vente_carburant_id: Optional[uuid.UUID] = None  # UUID
    pompiste: str  # Nom du pompiste
    montant_du: float
    montant_paye: Optional[float] = 0
    created_at: datetime
    date_echeance: Optional[datetime] = None
    utilisateur_gestion_id: uuid.UUID  # UUID

    class Config:
        from_attributes = True

class CreanceEmployeUpdate(BaseModel):
    montant_paye: Optional[float] = None
    date_echeance: Optional[datetime] = None
    statut: Optional[str] = None  # en_cours, payé, partiellement_payé

    class Config:
        from_attributes = True