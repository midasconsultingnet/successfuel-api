from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class JournalModificationTiersBase(BaseModel):
    tiers_id: uuid.UUID
    utilisateur_id: uuid.UUID
    champ_modifie: str
    valeur_precedente: Optional[str] = None
    valeur_nouvelle: Optional[str] = None
    type_modification: str
    ip_modification: Optional[str] = None
    user_agent: Optional[str] = None
    donnees_completes_avant: Optional[dict] = None
    donnees_completes_apres: Optional[dict] = None

    class Config:
        from_attributes = True


class JournalModificationTiersCreate(JournalModificationTiersBase):
    pass


class JournalModificationTiersUpdate(BaseModel):
    champ_modifie: Optional[str] = None
    valeur_precedente: Optional[str] = None
    valeur_nouvelle: Optional[str] = None
    type_modification: Optional[str] = None

    class Config:
        from_attributes = True


class JournalModificationTiersResponse(JournalModificationTiersBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True