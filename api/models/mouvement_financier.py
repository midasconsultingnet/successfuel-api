from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base_model import BaseModel

class Reglement(BaseModel):
    __tablename__ = "reglements"

    tiers_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    methode_paiement = Column(String)  # cash, cheque, virement, mobile_money, note_credit
    statut = Column(String, default="en_attente")  # en_attente, effectue, annule
    numero_piece_comptable = Column(String)
    date_echeance = Column(DateTime)
    penalites = Column(Float, default=0)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who recorded the payment
    compagnie_id = Column(String, nullable=False)  # UUID of the company
    station_id = Column(String, nullable=False)  # UUID of the station

class Creance(BaseModel):
    __tablename__ = "creances"

    tiers_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    date_echeance = Column(DateTime)
    statut = Column(String, default="active")  # active, recouvre, echeance, douteuse
    motif = Column(String)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who recorded the debt
    numero_piece_comptable = Column(String)
    penalites = Column(Float, default=0)
    compagnie_id = Column(String, nullable=False)  # UUID of the company
    station_id = Column(String, nullable=False)  # UUID of the station

class Avoir(BaseModel):
    __tablename__ = "avoirs"

    tiers_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    motif = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    statut = Column(String, default="emis")  # emis, utilise, partiellement_utilise, expire
    date_expiration = Column(DateTime)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who created the credit note
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company
    station_id = Column(String, nullable=False)  # UUID of the station
