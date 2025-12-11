from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from .base import Base

class Charge(Base):
    __tablename__ = "charges"
    
    station_id = Column(String, nullable=False)  # UUID of the station
    categorie = Column(String, nullable=False)  # electricite, eau, fournitures, maintenance, etc.
    fournisseur_id = Column(String, ForeignKey("tiers.id"))  # Optional - service provider
    date = Column(DateTime, nullable=False)
    montant = Column(Float, nullable=False)
    description = Column(String)
    date_echeance = Column(DateTime)
    statut = Column(String, default="prevu")  # prevu, echu, paye, en_cours_paiement
    methode_paiement = Column(String)  # cash, cheque, virement, mobile_money
    numero_piece_comptable = Column(String)
    utilisateur_id = Column(String, ForeignKey("utilisateur.id"))  # ID of the user who recorded the expense
    solde_du = Column(Float, default=0)  # Remaining amount to be paid
    compagnie_id = Column(String, nullable=False)  # UUID of the company

class CategorieCharge(Base):
    __tablename__ = "categories_charges"
    
    nom = Column(String, unique=True, nullable=False)
    description = Column(String)
    type = Column(String)  # fixe, variable
    seuil_alerte = Column(Float)  # Threshold for budget alerts
    compte_comptable = Column(String)  # Accounting account
    compagnie_id = Column(String, nullable=False)  # UUID of the company