from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel

class VenteCarburant(BaseModel):
    __tablename__ = "vente_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    pistolet_id = Column(UUID(as_uuid=True), ForeignKey("pistolet.id"), nullable=False)
    tresorerie_id = Column(UUID(as_uuid=True), ForeignKey("tresorerie.id"))  # Référence directe à la trésorerie utilisée pour le paiement
    quantite_vendue = Column(DECIMAL(12, 2), nullable=False)  # En litres - quantité effective débitée
    prix_unitaire = Column(DECIMAL(15, 2), nullable=False)
    montant_total = Column(DECIMAL(15, 2), nullable=False)
    date_vente = Column(DateTime(timezone=True), nullable=False)
    index_initial = Column(DECIMAL(12, 2), nullable=False)
    index_final = Column(DECIMAL(12, 2), nullable=False)
    quantite_mesuree = Column(DECIMAL(12, 2))  # En litres - calculée à partir des index (index_final - index_initial)
    ecart_quantite = Column(DECIMAL(12, 2))  # Différence entre quantite_vendue et quantite_mesuree
    besoin_compensation = Column(Boolean, default=False)  # Indique si une compensation est nécessaire
    compensation_id = Column(UUID(as_uuid=True), ForeignKey("avoirs.id"))  # Référence à l'avoir de compensation si nécessaire
    pompiste = Column(String, nullable=False)  # Nom du pompiste
    qualite_marshalle_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID du contrôleur qualité
    montant_paye = Column(DECIMAL(15, 2), default=0)
    mode_paiement = Column(String)  # espèce, chèque, carte crédit, note de crédit, crédit client
    statut = Column(String, default="enregistrée")  # "enregistrée", "validée", "annulée"
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    numero_piece_comptable = Column(String)
    creance_employe_id = Column(UUID(as_uuid=True), ForeignKey("creances_employes.id"))  # En cas de paiement insuffisant

    # Relations
    station = relationship("Station", lazy="select")
    cuve = relationship("Cuve", lazy="select")
    pistolet = relationship("Pistolet", lazy="select")
    tresorerie = relationship("Tresorerie", lazy="select")
    utilisateur = relationship("User", foreign_keys=[utilisateur_id], lazy="select")
    qualite_marshalle = relationship("User", foreign_keys=[qualite_marshalle_id], lazy="select")
    compensation = relationship("Avoir", lazy="select")
    creance_employe = relationship("CreanceEmploye", foreign_keys=[creance_employe_id], lazy="select")
