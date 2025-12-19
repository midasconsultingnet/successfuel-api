from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base_model import BaseModel

class Reglement(BaseModel):
    __tablename__ = "reglements"

    tiers_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    methode_paiement = Column(String)  # cash, cheque, virement, mobile_money, note_credit
    statut = Column(String, default="en_attente")  # en_attente, effectue, annule
    numero_piece_comptable = Column(String)
    date_echeance = Column(DateTime(timezone=True))
    penalites = Column(Float, default=0)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who recorded the payment
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the company
    station_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the station

class Creance(BaseModel):
    __tablename__ = "creances"

    tiers_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    date_echeance = Column(DateTime(timezone=True))
    statut = Column(String, default="active")  # active, recouvre, echeance, douteuse
    motif = Column(String)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who recorded the debt
    numero_piece_comptable = Column(String)
    penalites = Column(Float, default=0)
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the company
    station_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the station

class Avoir(BaseModel):
    __tablename__ = "avoirs"

    tiers_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant_initial = Column(Float, nullable=False)  # Montant initial de l'avoir
    montant_utilise = Column(Float, default=0)  # Montant déjà utilisé
    montant_restant = Column(Float)  # Montant restant (calculé)
    date_emission = Column(DateTime(timezone=True), nullable=False)  # Anciennement "date"
    date_utilisation = Column(DateTime(timezone=True))  # Date d'utilisation de l'avoir
    date_expiration = Column(DateTime(timezone=True))  # Date d'expiration de l'avoir
    motif = Column(String, nullable=False)  # Motif de l'émission de l'avoir
    statut = Column(String, default="emis")  # émis, utilisé, partiellement_utilisé, expiré
    utilisateur_emission_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who created the credit note
    utilisateur_utilisation_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who used the credit note
    reference_origine = Column(String, nullable=False)  # Référence d'origine de l'avoir
    module_origine = Column(String, nullable=False)  # Module d'origine : ventes, achats, compensations
    numero_piece_comptable = Column(String)
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the company
    station_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the station
