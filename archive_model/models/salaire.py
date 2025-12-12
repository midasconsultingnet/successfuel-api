from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from .base import Base

class Salaire(Base):
    __tablename__ = "salaires"
    
    employe_id = Column(String, ForeignKey("tiers.id"), nullable=False)  # Employee is a type of tier
    periode = Column(String, nullable=False)  # Format: YYYY-MM
    date_echeance = Column(DateTime, nullable=False)
    date_paiement = Column(DateTime)  # When was it paid
    salaire_base = Column(Float, nullable=False)
    montant_total = Column(Float, nullable=False)
    statut = Column(String, default="prevu")  # prevu, echu, paye, du
    methode_paiement = Column(String)  # cash, virement, cheque
    utilisateur_id = Column(String, ForeignKey("utilisateur.id"))  # ID of the user who processed the payment
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company
    station_id = Column(String, nullable=False)  # UUID of the station

class Prime(Base):
    __tablename__ = "primes"
    
    employe_id = Column(String, ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    motif = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    periode = Column(String)  # Optional: to which period does this bonus apply
    utilisateur_id = Column(String, ForeignKey("utilisateur.id"))  # ID of the user who created the bonus
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company

class Avance(Base):
    __tablename__ = "avances"
    
    employe_id = Column(String, ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    motif = Column(String)
    date_echeance = Column(DateTime)  # When should it be repaid
    montant_rembourse = Column(Float, default=0)  # Amount repaid so far
    statut = Column(String, default="non_rembourse")  # non_rembourse, en_cours, rembourse
    utilisateur_id = Column(String, ForeignKey("utilisateur.id"))  # ID of the user who created the advance
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company