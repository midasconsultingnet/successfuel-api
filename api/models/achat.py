from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from .base import Base

class Achat(Base):
    __tablename__ = "achats"
    
    fournisseur_id = Column(String, ForeignKey("tiers.id"), nullable=False)
    station_id = Column(String, nullable=False)  # UUID of the station
    date = Column(DateTime, nullable=False)
    numero_bl = Column(String)  # Bon de livraison number
    numero_facture = Column(String)
    date_facturation = Column(DateTime)
    montant_total = Column(Float, nullable=False)
    statut = Column(String, default="brouillon")  # brouillon, valide, facture, paye
    type_paiement = Column(String)  # prepaye, cod, differe, consignation, mixte
    delai_paiement = Column(Integer)  # in days
    pourcentage_acompte = Column(Float)  # e.g., 30% before delivery
    limite_credit = Column(Float)
    mode_reglement = Column(String)  # cash, cheque, virement, mobile_money
    documents_requis = Column(String)  # JSON string of required documents
    compagnie_id = Column(String, nullable=False)  # UUID of the company

class AchatDetail(Base):
    __tablename__ = "achats_details"
    
    achat_id = Column(String, ForeignKey("achats.id"), nullable=False)
    produit_id = Column(String, ForeignKey("produits.id"), nullable=False)
    quantite_demandee = Column(Integer, nullable=False)
    quantite_recue = Column(Integer, default=0)
    quantite_facturee = Column(Integer, default=0)
    prix_unitaire_demande = Column(Float, nullable=False)
    prix_unitaire_recu = Column(Float)  # Updated when received
    prix_unitaire_facture = Column(Float)  # Updated when invoiced
    montant = Column(Float, nullable=False)