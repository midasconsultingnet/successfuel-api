from sqlalchemy import Column, String, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from .base_model import BaseModel
import uuid


class VueVentesBoutique(BaseModel):
    __tablename__ = 'vue_ventes_boutique'

    id = Column(UUID(as_uuid=True), primary_key=True)
    station_id = Column(UUID(as_uuid=True))
    station_nom = Column(String)
    client_id = Column(UUID(as_uuid=True))
    client_nom = Column(String)
    date_vente = Column(DateTime)
    montant_total = Column(DECIMAL(10, 2))
    type_vente = Column(String)
    statut = Column(String)
    utilisateur_id = Column(UUID(as_uuid=True))
    utilisateur_nom = Column(String)
    utilisateur_prenom = Column(String)
    tresorerie_id = Column(UUID(as_uuid=True))
    trésorerie_nom = Column(String)