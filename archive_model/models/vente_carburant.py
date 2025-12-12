from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class VenteCarburant(Base):
    __tablename__ = "vente_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    pistolet_id = Column(UUID(as_uuid=True), ForeignKey("pistolet.id"), nullable=False)
    trésorerie_station_id = Column(UUID(as_uuid=True), ForeignKey("tresorerie_station.id"))  # Référence à la trésorerie utilisée pour le paiement
    quantite_vendue = Column(DECIMAL(12, 2), nullable=False)  # En litres
    prix_unitaire = Column(DECIMAL(15, 2), nullable=False)
    montant_total = Column(DECIMAL(15, 2), nullable=False)
    date_vente = Column(DateTime, nullable=False)
    index_initial = Column(DECIMAL(12, 2), nullable=False)
    index_final = Column(DECIMAL(12, 2), nullable=False)
    pompiste = Column(String, nullable=False)  # Nom du pompiste
    qualite_marshalle_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID du contrôleur qualité
    montant_paye = Column(DECIMAL(15, 2), default=0)
    mode_paiement = Column(String)  # espèce, chèque, carte crédit, note de crédit, crédit client
    statut = Column(String, default="enregistrée")  # "enregistrée", "validée", "annulée"
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    numero_piece_comptable = Column(String)
    creance_employe_id = Column(UUID(as_uuid=True), ForeignKey("creances_employes.id"))  # En cas de paiement insuffisant