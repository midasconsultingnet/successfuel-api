from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class CreanceEmploye(BaseModel):
    __tablename__ = "creances_employes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vente_carburant_id = Column(UUID(as_uuid=True), ForeignKey("vente_carburant.id"))
    pompiste = Column(String, nullable=False)  # Nom du pompiste
    montant_du = Column(DECIMAL(15, 2), nullable=False)
    montant_paye = Column(DECIMAL(15, 2), default=0)
    solde_creance = Column(DECIMAL(15, 2), nullable=False)
    date_echeance = Column(DateTime)
    statut = Column(String, default="en_cours")  # "en_cours", "payé", "partiellement_payé"
    utilisateur_gestion_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
