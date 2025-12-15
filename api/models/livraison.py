from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class Livraison(BaseModel):
    __tablename__ = "livraisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # UUID of the station
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)  # ID of the tank
    carburant_id = Column(String, nullable=False)  # UUID of the fuel type
    quantite_livree = Column(Integer, nullable=False)  # in liters
    date = Column(DateTime, nullable=False)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"))  # Optional - supplier of the delivery
    numero_bl = Column(String)  # Delivery note number
    numero_facture = Column(String)  # Invoice number
    prix_unitaire = Column(Float)  # Price per liter
    montant_total = Column(Float)  # Total amount
    jauge_avant = Column(Integer)  # Tank level before delivery
    jauge_apres = Column(Integer)  # Tank level after delivery
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who recorded the delivery
    commentaires = Column(String)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)  # UUID of the company
