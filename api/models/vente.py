from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from .base import Base

class Vente(Base):
    __tablename__ = "ventes"
    
    station_id = Column(String, nullable=False)  # UUID of the station
    client_id = Column(String, ForeignKey("tiers.id"))  # Optional - for credit sales
    date = Column(DateTime, nullable=False)
    montant_total = Column(Float, nullable=False)
    statut = Column(String, default="en_cours")  # en_cours, terminee, annulee
    type_vente = Column(String, default="produit")  # produit, service, hybride
    trésorerie_id = Column(String, ForeignKey("tresoreries.id"))  # ID of the cash register used
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company

class VenteDetail(Base):
    __tablename__ = "ventes_details"
    
    vente_id = Column(String, ForeignKey("ventes.id"), nullable=False)
    produit_id = Column(String, ForeignKey("produits.id"), nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant = Column(Float, nullable=False)
    remise = Column(Float, default=0)