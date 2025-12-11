from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class Inventaire(Base):
    __tablename__ = "inventaires"
    
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # UUID of the station
    produit_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"))  # For boutique inventory
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"))  # For fuel tank inventory
    quantite_reelle = Column(Integer)  # Physical count
    date = Column(DateTime, nullable=False)
    statut = Column(String, default="brouillon")  # brouillon, en_cours, termine, valide, rapproche, cloture
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who performed the count
    commentaires = Column(String)
    ecart = Column(Integer)  # Calculated difference (reel - theorique)
    type_ecart = Column(String)  # perte, surplus, erreur, anomalie
    seuil_tolerance = Column(Float, default=0)  # Tolerance threshold for alerts
    methode_mesure = Column(String, default="manuel")  # manuel, jauge_digitale, sonde_automatique (for fuel)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)  # UUID of the company