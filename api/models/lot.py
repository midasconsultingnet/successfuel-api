from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel
from sqlalchemy.orm import relationship

class Lot(BaseModel):
    __tablename__ = "lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produit_id = Column(UUID(as_uuid=True), ForeignKey("produit.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # Ajout du lien avec Station
    numero_lot = Column(String(100), nullable=False)  # Numéro ou code du lot
    date_fabrication = Column(DateTime)  # Remplacement de date_production
    date_limite_consommation = Column(DateTime)  # Remplacement de date_peremption
    quantite = Column(Float, nullable=False)  # Quantité dans ce lot
    statut = Column(String(20), default="actif")  # actif, expiré, vendu, etc.

    # Relations
    produit = relationship("Produit", back_populates="lots")
    station = relationship("Station", back_populates="lots")  # Ajout de la relation avec Station
