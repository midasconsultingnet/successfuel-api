from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from .base_model import BaseModel

class StatutInventaire(PyEnum):
    BROUILLON = "brouillon"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    VALIDE = "valide"
    RAPPORCHE = "rapproche"
    CLOTURE = "cloture"

class Inventaire(BaseModel):
    __tablename__ = "inventaires"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # UUID of the station
    produit_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"))  # For boutique inventory
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"))  # For fuel tank inventory
    quantite_reelle = Column(Float)  # Physical count
    date = Column(DateTime(timezone=True), nullable=False)
    statut = Column(String, default=StatutInventaire.BROUILLON.value)  # Updated with new statuses
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who performed the count
    commentaires = Column(String)
    ecart = Column(Float)  # Calculated difference (reel - theorique)
    type_ecart = Column(String)  # perte, surplus, erreur, anomalie
    seuil_tolerance = Column(Float, default=0)  # Tolerance threshold for alerts
    methode_mesure = Column(String, default="manuel")  # manuel, jauge_digitale, sonde_automatique (for fuel)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)  # UUID of the company

    # Relations
    ecarts = relationship("EcartInventaire", back_populates="inventaire")
