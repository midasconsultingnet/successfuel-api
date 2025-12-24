from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AchatDetailCreate(BaseModel):
    produit_id: str  # UUID
    quantite_demandee: int
    prix_unitaire_demande: float
    montant: float

class AchatDetailUpdate(BaseModel):
    quantite_demandee: Optional[int] = None
    prix_unitaire_demande: Optional[float] = None
    montant: Optional[float] = None

class AchatCreate(BaseModel):
    fournisseur_id: str  # UUID
    date: datetime
    numero_bl: Optional[str] = None
    numero_facture: Optional[str] = None
    date_facturation: Optional[datetime] = None
    type_paiement: str  # prepaye, cod, differe, consignation, mixte
    delai_paiement: Optional[int] = None  # in days
    pourcentage_acompte: Optional[float] = None  # e.g., 30% before delivery
    limite_credit: Optional[float] = None
    mode_reglement: Optional[str] = None  # cash, cheque, virement, mobile_money
    documents_requis: Optional[str] = None  # JSON string of required documents
    details: List[AchatDetailCreate]
    station_id: str  # UUID of the station
    tresorerie_station_id: str  # UUID of the treasury station
    compagnie_id: str  # UUID of the company

class AchatUpdate(BaseModel):
    fournisseur_id: Optional[str] = None
    date: Optional[datetime] = None
    numero_bl: Optional[str] = None
    numero_facture: Optional[str] = None
    date_facturation: Optional[datetime] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None  # brouillon, valide, facture, paye
    type_paiement: Optional[str] = None
    delai_paiement: Optional[int] = None
    pourcentage_acompte: Optional[float] = None
    limite_credit: Optional[float] = None
    mode_reglement: Optional[str] = None
    documents_requis: Optional[str] = None

# Schémas pour les achats de carburant
class AchatCarburantCreate(BaseModel):
    fournisseur_id: str  # UUID
    date_achat: datetime
    numero_bl: str
    numero_facture: str
    montant_total: float
    station_id: str  # UUID
    utilisateur_id: str  # UUID
    quantite_theorique: Optional[float] = None  # Quantité théorique pour les compensations
    quantite_reelle: Optional[float] = None   # Quantité réelle pour les compensations

class AchatCarburantUpdate(BaseModel):
    numero_bl: Optional[str] = None
    numero_facture: Optional[str] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None  # brouillon, validé, facturé, annulé
    utilisateur_id: Optional[str] = None

class LigneAchatCarburantCreate(BaseModel):
    achat_carburant_id: str  # UUID
    carburant_id: str  # UUID
    quantite: float
    prix_unitaire: float
    montant: float
    cuve_id: str  # UUID

class CompensationFinanciereCreate(BaseModel):
    achat_carburant_id: str  # UUID
    type_compensation: str  # "avoir_reçu", "avoir_dû"
    quantite_theorique: float
    quantite_reelle: float
    difference: float
    montant_compensation: float
    motif: Optional[str] = None

class AvoirCompensationCreate(BaseModel):
    compensation_financiere_id: str  # UUID
    tiers_id: str  # UUID
    montant: float
    motif: str
    utilisateur_emission_id: str  # UUID

class AchatDetailResponse(BaseModel):
    id: str  # UUID
    produit_id: str  # UUID
    quantite_demandee: int
    prix_unitaire_demande: float
    montant: float

class AchatResponse(BaseModel):
    id: str  # UUID
    fournisseur_id: str  # UUID
    date: datetime
    numero_bl: Optional[str] = None
    numero_facture: Optional[str] = None
    date_facturation: Optional[datetime] = None
    montant_total: float
    statut: str  # brouillon, valide, facture, paye
    type_paiement: str  # prepaye, cod, differe, consignation, mixte
    delai_paiement: Optional[int] = None  # in days
    pourcentage_acompte: Optional[float] = None  # e.g., 30% before delivery
    limite_credit: Optional[float] = None
    mode_reglement: Optional[str] = None  # cash, cheque, virement, mobile_money
    documents_requis: Optional[str] = None  # JSON string of required documents
    station_id: str  # UUID of the station
    tresorerie_station_id: Optional[str]  # UUID of the treasury station
    compagnie_id: str  # UUID of the company

class AchatCarburantResponse(BaseModel):
    id: str  # UUID
    fournisseur_id: str  # UUID
    date_achat: datetime
    numero_bl: str
    numero_facture: str
    montant_total: float
    statut: str  # brouillon, validé, facturé, annulé
    station_id: str  # UUID
    utilisateur_id: str  # UUID
    quantite_theorique: Optional[float] = None  # Quantité théorique pour les compensations
    quantite_reelle: Optional[float] = None   # Quantité réelle pour les compensations

class LigneAchatCarburantResponse(BaseModel):
    id: str  # UUID
    achat_carburant_id: str  # UUID
    carburant_id: str  # UUID
    quantite: float
    prix_unitaire: float
    montant: float
    cuve_id: str  # UUID

class CompensationFinanciereResponse(BaseModel):
    id: str  # UUID
    achat_carburant_id: str  # UUID
    type_compensation: str  # "avoir_reçu", "avoir_dû"
    quantite_theorique: float
    quantite_reelle: float
    difference: float
    montant_compensation: float
    motif: Optional[str] = None

class AvoirCompensationResponse(BaseModel):
    id: str  # UUID
    compensation_financiere_id: str  # UUID
    tiers_id: str  # UUID
    montant: float
    motif: str
    utilisateur_emission_id: str  # UUID