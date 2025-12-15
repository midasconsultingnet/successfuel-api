from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class ImmobilisationCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    code: str
    type: str  # "matériel", "véhicule", "bâtiment", etc.
    date_acquisition: datetime
    valeur_origine: float
    station_id: uuid.UUID  # UUID

class ImmobilisationResponse(ImmobilisationCreate):
    id: uuid.UUID
    valeur_nette: Optional[float] = None
    taux_amortissement: Optional[float] = None
    duree_vie: Optional[int] = None
    statut: str = "actif"  # "actif", "inactif", "cessionné", "hors_service"
    created_at: datetime
    updated_at: datetime

class ImmobilisationUpdate(BaseModel):
    description: Optional[str] = None
    type: Optional[str] = None
    valeur_origine: Optional[float] = None
    valeur_nette: Optional[float] = None
    taux_amortissement: Optional[float] = None
    duree_vie: Optional[int] = None
    statut: Optional[str] = None  # "actif", "inactif", "cessionné", "hors_service"

class MouvementImmobilisationCreate(BaseModel):
    immobilisation_id: uuid.UUID  # UUID
    type_mouvement: str  # "acquisition", "amélioration", "cession", "sortie", "amortissement"
    date_mouvement: datetime
    description: Optional[str] = None
    valeur_variation: Optional[float] = None
    valeur_apres_mouvement: Optional[float] = None
    utilisateur_id: uuid.UUID  # UUID
    reference_document: Optional[str] = None

class MouvementImmobilisationResponse(MouvementImmobilisationCreate):
    id: uuid.UUID
    statut: str = "validé"  # "validé", "annulé"
    created_at: datetime
    updated_at: datetime