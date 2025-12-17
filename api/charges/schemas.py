from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class PaiementChargeCreate(BaseModel):
    charge_id: UUID
    date_paiement: Optional[datetime] = None
    montant_paye: float
    methode_paiement: Optional[str] = None
    reference_paiement: Optional[str] = None
    commentaire: Optional[str] = None
    compagnie_id: str


class PaiementChargeUpdate(BaseModel):
    date_paiement: Optional[datetime] = None
    montant_paye: Optional[float] = None
    methode_paiement: Optional[str] = None
    reference_paiement: Optional[str] = None
    commentaire: Optional[str] = None


class PaiementChargeResponse(BaseModel):
    id: UUID
    charge_id: UUID
    date_paiement: datetime
    montant_paye: float
    methode_paiement: Optional[str]
    reference_paiement: Optional[str]
    utilisateur_id: Optional[UUID]
    commentaire: Optional[str]
    compagnie_id: str
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True


class ChargeCreate(BaseModel):
    station_id: str
    categorie: str
    fournisseur_id: Optional[UUID] = None
    date: datetime
    montant: float
    description: Optional[str] = None
    date_echeance: Optional[datetime] = None
    methode_paiement: Optional[str] = None
    numero_piece_comptable: Optional[str] = None
    compagnie_id: str
    paiement_initial: Optional[PaiementChargeCreate] = None  # Pour permettre un paiement initial lors de la création

    # Champs pour les charges récurrentes
    est_recurrente: Optional[bool] = False
    frequence_recurrence: Optional[str] = None  # quotidienne, hebdomadaire, mensuelle, etc.
    date_prochaine_occurrence: Optional[date] = None
    seuil_alerte: Optional[float] = None
    arret_compte: Optional[bool] = False


class ChargeUpdate(BaseModel):
    station_id: Optional[str] = None
    categorie: Optional[str] = None
    fournisseur_id: Optional[UUID] = None
    date: Optional[datetime] = None
    montant: Optional[float] = None
    description: Optional[str] = None
    date_echeance: Optional[datetime] = None
    statut: Optional[str] = None
    methode_paiement: Optional[str] = None
    numero_piece_comptable: Optional[str] = None
    solde_du: Optional[float] = None

    # Champs pour les charges récurrentes
    est_recurrente: Optional[bool] = None
    frequence_recurrence: Optional[str] = None
    date_prochaine_occurrence: Optional[date] = None
    seuil_alerte: Optional[float] = None
    arret_compte: Optional[bool] = None


class ChargeResponse(BaseModel):
    id: UUID
    station_id: str
    categorie: str
    fournisseur_id: Optional[UUID]
    date: datetime
    montant: float
    description: Optional[str]
    date_echeance: Optional[datetime]
    statut: str
    methode_paiement: Optional[str]
    numero_piece_comptable: Optional[str]
    utilisateur_id: Optional[UUID]
    solde_du: float
    compagnie_id: str
    date_creation: datetime
    date_modification: datetime

    # Champs pour les charges récurrentes
    est_recurrente: bool
    frequence_recurrence: Optional[str]
    date_prochaine_occurrence: Optional[date]
    seuil_alerte: Optional[float]
    arret_compte: bool

    class Config:
        from_attributes = True