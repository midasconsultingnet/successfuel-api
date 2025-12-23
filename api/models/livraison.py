from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class Livraison(BaseModel):
    __tablename__ = "livraisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_carburant_id = Column(UUID(as_uuid=True), ForeignKey("achat_carburant.id"), nullable=True)  # Reference to fuel purchase
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # UUID of the station
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)  # ID of the tank
    carburant_id = Column(UUID(as_uuid=True), ForeignKey("carburant.id"), nullable=False)  # UUID of the fuel type
    quantite_livree = Column(DECIMAL(12, 2), nullable=False)  # Quantity delivered (was: quantite_livree)
    quantite_commandee = Column(DECIMAL(12, 2), nullable=True)  # Quantity ordered (new)
    date_livraison = Column(DateTime(timezone=True), nullable=False)  # Date of delivery (was: date)
    prix_unitaire = Column(DECIMAL(15, 2), nullable=True)  # Price per liter
    montant_total = Column(DECIMAL(15, 2), nullable=True)  # Total amount
    jauge_avant_livraison = Column(DECIMAL(12, 2), nullable=True)  # Tank level before delivery (was: jauge_avant)
    jauge_apres_livraison = Column(DECIMAL(12, 2), nullable=True)  # Tank level after delivery (was: jauge_apres)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)  # ID of the user who recorded the delivery
    information = Column(JSON, nullable=True)  # Information in JSON format (was: numero_bl)
    numero_facture = Column(String, nullable=True)  # Invoice number
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)  # UUID of the company
    statut_livraison = Column(String, default="en_attente")  # Status of delivery: en_attente, en_cours, livre_completement, livre_partiellement, en_retard (new)
