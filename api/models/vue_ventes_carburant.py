from sqlalchemy import Column, String, DateTime, DECIMAL, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from .base_model import BaseModel
import uuid


class VueVentesCarburant(BaseModel):
    __tablename__ = 'vue_ventes_carburant'

    id = Column(UUID(as_uuid=True), primary_key=True)
    station_id = Column(UUID(as_uuid=True))
    station_nom = Column(String)
    carburant_id = Column(UUID(as_uuid=True))
    carburant_libelle = Column(String)
    cuve_id = Column(UUID(as_uuid=True))
    cuve_nom = Column(String)
    pistolet_id = Column(UUID(as_uuid=True))
    quantite_vendue = Column(DECIMAL(10, 2))
    prix_unitaire = Column(DECIMAL(10, 2))
    montant_total = Column(DECIMAL(10, 2))
    date_vente = Column(DateTime)
    index_initial = Column(DECIMAL(10, 2))
    index_final = Column(DECIMAL(10, 2))
    pompiste = Column(String)
    utilisateur_nom = Column(String)
    utilisateur_prenom = Column(String)
    mode_paiement = Column(String)
    statut = Column(String)