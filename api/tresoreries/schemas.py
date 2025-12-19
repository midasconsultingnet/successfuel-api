from pydantic import BaseModel
from typing import Optional, Any, Dict, Union
from datetime import datetime
import uuid

class TresorerieBase(BaseModel):
    nom: str
    type: str  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde_initial: float
    devise: Optional[str] = "XOF"
    informations_bancaires: Optional[Union[Dict[str, Any], str]] = None  # JSONB for bank details
    statut: Optional[str] = "actif"  # actif, inactif
    compagnie_id: uuid.UUID

    class Config:
        from_attributes = True

class TresorerieCreate(BaseModel):
    nom: str
    type: str  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde_initial: float
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
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TresorerieStationBase(BaseModel):
    tresorerie_id: uuid.UUID
    station_id: uuid.UUID
    solde_initial: float

    class Config:
        from_attributes = True

class TresorerieStationCreate(TresorerieStationBase):
    pass

class TresorerieStationUpdate(BaseModel):
    solde_initial: Optional[float] = None

    class Config:
        from_attributes = True

class TresorerieStationResponse(TresorerieStationBase):
    id: uuid.UUID
    solde_actuel: float
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
    coordonnees_gps: Optional[str] = None
    statut_station: Optional[str] = "inactif"
    config: Optional[Any] = None

    # Champs de Tresorerie
    tresorerie_id: uuid.UUID
    nom_tresorerie: str
    type_tresorerie: str
    solde_initial_tresorerie: float
    devise: Optional[str] = "XOF"
    informations_bancaires: Optional[Union[Dict[str, Any], str]] = None  # JSONB for bank details
    statut_tresorerie: Optional[str] = "actif"

    # Champs de TresorerieStation
    tresorerie_station_id: uuid.UUID
    solde_initial_station: float
    solde_actuel: float

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
    tresorerie_station_id: uuid.UUID
    type_mouvement: str  # entrée, sortie
    montant: float
    date_mouvement: datetime
    description: Optional[str] = None
    module_origine: str
    reference_origine: str
    utilisateur_id: uuid.UUID
    numero_piece_comptable: Optional[str] = None
    statut: Optional[str] = "validé"  # validé, annulé
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
    utilisateur_id: uuid.UUID
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

    class Config:
        from_attributes = True