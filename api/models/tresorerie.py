from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from .base import Base

class Tresorerie(Base):
    __tablename__ = "tresoreries"
    
    nom = Column(String, nullable=False)
    type = Column(String, nullable=False)  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde = Column(Float, default=0)
    statut = Column(Boolean, default=True)  # Actif/inactif
    informations_bancaires = Column(String)  # JSON string for bank details
    compagnie_id = Column(String, nullable=False)  # UUID of the company
    station_id = Column(String, nullable=False)  # UUID of the station this treasury belongs to

class Transfert(Base):
    __tablename__ = "transferts"
    
    tresorerie_source_id = Column(String, ForeignKey("tresoreries.id"), nullable=False)
    tresorerie_destination_id = Column(String, ForeignKey("tresoreries.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String)
    utilisateur_id = Column(String, ForeignKey("utilisateur.id"))  # ID of the user who made the transfer
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company