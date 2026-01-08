from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, Union
from datetime import datetime
import uuid


class CoordonneesGPS(BaseModel):
    lat: float
    long: float

class TresorerieBase(BaseModel):
    nom: str
    type: str  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde_initial: Optional[float] = None  # Optionnel, défini lors de la création de la trésorerie
    devise: Optional[str] = "XOF"
    informations_bancaires: Optional[Union[Dict[str, Any], str]] = None  # JSONB for bank details
    statut: Optional[str] = "actif"  # actif, inactif
    compagnie_id: uuid.UUID

    class Config:
        from_attributes = True

class TresorerieCreate(BaseModel):
    nom: str
    type: str  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde_initial: Optional[float] = None  # Optionnel, défini lors de la création de la trésorerie
    devise: Optional[str] = "XOF"
    informations_bancaires: Optional[Union[Dict[str, Any], str]] = None  # JSONB for bank details
    statut: Optional[str] = "actif"  # actif, inactif

    class Config:
        from_attributes = True

class TresorerieUpdate(BaseModel):
    nom: Optional[str] = None
    type: Optional[str] = None
    solde_initial: Optional[float] = None
    devise: Optional[str] = None
    informations_bancaires: Optional[Union[Dict[str, Any], str]] = None  # JSONB for bank details
    statut: Optional[str] = None

    class Config:
        from_attributes = True

class TresorerieResponse(TresorerieBase):
    id: uuid.UUID
    solde_tresorerie: float  # Solde global calculé à partir des mouvements
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TresorerieStationBase(BaseModel):
    tresorerie_id: uuid.UUID
    station_id: uuid.UUID

    class Config:
        from_attributes = True

class TresorerieStationCreate(TresorerieStationBase):
    pass

class TresorerieStationUpdate(BaseModel):
    pass

    class Config:
        from_attributes = True

class TresorerieStationResponse(TresorerieStationBase):
    id: uuid.UUID
    # Le solde_actuel est maintenant géré via la vue matérialisée vue_solde_tresorerie_station
    # et sera fourni dans les réponses spécifiques qui en ont besoin
    created_at: datetime

    class Config:
        from_attributes = True


class StationTresorerieResponse(BaseModel):
    # Champs de Station
    station_id: uuid.UUID
    compagnie_id: uuid.UUID
    nom_station: str
    code: str
    adresse: Optional[str] = None
    coordonnees_gps: Optional[CoordonneesGPS] = None
    statut_station: Optional[str] = "inactif"
    config: Optional[Any] = None

    # Champs de Tresorerie
    tresorerie_id: uuid.UUID
    nom_tresorerie: str
    type_tresorerie: str
    solde_initial_tresorerie: float
    solde_tresorerie: float  # Solde global de la trésorerie
    devise: Optional[str] = "XOF"
    informations_bancaires: Optional[Union[Dict[str, Any], str]] = None  # JSONB for bank details
    statut_tresorerie: Optional[str] = "actif"

    # Champs de TresorerieStation
    tresorerie_station_id: uuid.UUID
    solde_actuel_station: float  # Solde de la trésorerie pour cette station spécifique

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EtatInitialTresorerieBase(BaseModel):
    tresorerie_station_id: uuid.UUID
    date_enregistrement: datetime
    montant: float
    commentaire: Optional[str] = None
    enregistre_par: uuid.UUID

    class Config:
        from_attributes = True

class EtatInitialTresorerieCreate(EtatInitialTresorerieBase):
    pass

class EtatInitialTresorerieUpdate(BaseModel):
    montant: Optional[float] = None
    commentaire: Optional[str] = None

    class Config:
        from_attributes = True

class EtatInitialTresorerieResponse(EtatInitialTresorerieBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MouvementTresorerieBase(BaseModel):
    tresorerie_station_id: Optional[uuid.UUID] = None  # Peut être NULL pour les mouvements liés directement à une trésorerie
    tresorerie_globale_id: Optional[uuid.UUID] = None  # Nouveau champ pour lier directement à une trésorerie
    station_id: Optional[uuid.UUID] = None  # Pour les mouvements globaux liés à une station
    type_mouvement: str  # entrée, sortie
    montant: float
    date_mouvement: datetime
    description: Optional[str] = None
    module_origine: str
    reference_origine: str
    utilisateur_id: Optional[uuid.UUID] = None  # Rendu optionnel car défini automatiquement
    numero_piece_comptable: Optional[str] = None
    statut: Optional[str] = "validé"  # validé, annulé
    est_annule: Optional[bool] = False  # Nouveau champ pour la gestion des annulations
    mouvement_origine_id: Optional[uuid.UUID] = None  # Référence vers le mouvement original en cas d'annulation
    methode_paiement_id: Optional[uuid.UUID] = None  # Ajout de la méthode de paiement

    class Config:
        from_attributes = True

class MouvementTresorerieCreate(MouvementTresorerieBase):
    pass

class MouvementTresorerieUpdate(BaseModel):
    type_mouvement: Optional[str] = None
    montant: Optional[float] = None
    description: Optional[str] = None
    numero_piece_comptable: Optional[str] = None
    statut: Optional[str] = None
    methode_paiement_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

class MouvementTresorerieResponse(MouvementTresorerieBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class TransfertTresorerieBase(BaseModel):
    tresorerie_source_id: uuid.UUID
    tresorerie_destination_id: uuid.UUID
    montant: float
    date_transfert: datetime
    description: Optional[str] = None
    utilisateur_id: Optional[uuid.UUID] = None  # Rendu optionnel car défini automatiquement
    statut: Optional[str] = "validé"  # validé, annulé

    class Config:
        from_attributes = True

class TransfertTresorerieCreate(TransfertTresorerieBase):
    pass

class TransfertTresorerieUpdate(BaseModel):
    description: Optional[str] = None
    statut: Optional[str] = None

    class Config:
        from_attributes = True

class TransfertTresorerieResponse(TransfertTresorerieBase):
    id: uuid.UUID
    nom_tresorerie_source: Optional[str] = None
    nom_tresorerie_destination: Optional[str] = None

    class Config:
        from_attributes = True

class TresorerieSoldeResponse(BaseModel):
    id: uuid.UUID
    nom: str
    type: str  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde_initial: float
    solde_tresorerie: float  # Solde global calculé à partir des mouvements
    devise: Optional[str] = "XOF"
    informations_bancaires: Optional[Union[Dict[str, Any], str]] = None  # JSONB for bank details
    statut: Optional[str] = "actif"  # actif, inactif
    compagnie_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True