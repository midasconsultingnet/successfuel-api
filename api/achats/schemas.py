from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AchatDetailCreate(BaseModel):
    produit_id: str  # UUID
    quantite_demandee: int
    prix_unitaire_demande: float
    montant: float

class AchatDetailUpdate(BaseModel):
    quantite_demandee: Optional[int] = None
    prix_unitaire_demande: Optional[float] = None
    montant: Optional[float] = None


class AchatDetailCorrection(BaseModel):
    ancienne_quantite: Optional[int] = None
    nouvelle_quantite: Optional[int] = None
    ancien_prix_unitaire: Optional[float] = None
    nouveau_prix_unitaire: Optional[float] = None
    motif_correction: str = Field(..., max_length=500)

class AchatCreate(BaseModel):
    fournisseur_id: str  # UUID
    date: datetime
    informations: Optional[dict] = None  # JSON field for additional information like numero_bl, numero_facture, etc.
    type_paiement: str  # prepaye, cod, differe, consignation, mixte
    delai_paiement: Optional[int] = None  # in days
    mode_reglement: Optional[str] = None  # cash, cheque, virement, mobile_money
    details: List[AchatDetailCreate]
    station_id: str  # UUID of the station
    tresorerie_id: str  # UUID of the treasury (either station or global treasury)

class AchatUpdate(BaseModel):
    fournisseur_id: Optional[str] = None
    date: Optional[datetime] = None
    informations: Optional[dict] = None  # JSON field for additional information
    montant_total: Optional[float] = None
    statut: Optional[str] = None  # brouillon, valide, facture, paye
    type_paiement: Optional[str] = None
    delai_paiement: Optional[int] = None
    mode_reglement: Optional[str] = None

class ProduitResponse(BaseModel):
    id: UUID
    nom: str
    code: str
    code_barre: str
    description: Optional[str] = None
    unite_mesure: str
    type: str
    famille_id: Optional[UUID] = None
    compagnie_id: UUID
    has_stock: bool

    class Config:
        from_attributes = True


class AchatDetailResponse(BaseModel):
    id: UUID  # UUID
    produit_id: UUID  # UUID
    produit: ProduitResponse  # Information complète sur le produit
    quantite_demandee: int
    prix_unitaire_demande: float
    montant: float

class AchatResponse(BaseModel):
    id: UUID4  # UUID
    fournisseur_id: UUID4  # UUID
    date: datetime
    informations: Optional[dict] = None  # JSON field for additional information
    montant_total: float
    statut: str  # brouillon, valide, facture, paye
    type_paiement: str  # prepaye, cod, differe, consignation, mixte
    delai_paiement: Optional[int] = None  # in days
    mode_reglement: Optional[str] = None  # cash, cheque, virement, mobile_money
    station_id: UUID4  # UUID of the station
    tresorerie_id: Optional[UUID4]  # UUID of the treasury (either station or global treasury)
    compagnie_id: UUID4  # UUID of the company
    date_livraison_prevue: Optional[datetime] = None

    class Config:
        from_attributes = True

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

class AchatCarburantResponse(BaseModel):
    id: UUID4  # UUID
    fournisseur_id: UUID4  # UUID
    date_achat: datetime
    numero_bl: str
    numero_facture: str
    montant_total: float
    statut: str  # brouillon, validé, facturé, annulé
    station_id: UUID4  # UUID
    utilisateur_id: UUID4  # UUID
    quantite_theorique: Optional[float] = None  # Quantité théorique pour les compensations
    quantite_reelle: Optional[float] = None   # Quantité réelle pour les compensations

class LigneAchatCarburantResponse(BaseModel):
    id: UUID4  # UUID
    achat_carburant_id: UUID4  # UUID
    carburant_id: UUID4  # UUID
    quantite: float
    prix_unitaire: float
    montant: float
    cuve_id: UUID4  # UUID

class CompensationFinanciereResponse(BaseModel):
    id: UUID4  # UUID
    achat_carburant_id: UUID4  # UUID
    type_compensation: str  # "avoir_reçu", "avoir_dû"
    quantite_theorique: float
    quantite_reelle: float
    difference: float
    montant_compensation: float
    motif: Optional[str] = None

class AvoirCompensationResponse(BaseModel):
    id: UUID4  # UUID
    compensation_financiere_id: UUID4  # UUID
    tiers_id: UUID4  # UUID
    montant: float
    motif: str
    utilisateur_emission_id: UUID4  # UUID