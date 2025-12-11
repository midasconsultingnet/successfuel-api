from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean
from .base import Base

class Tiers(Base):
    __tablename__ = "tiers"
    
    nom = Column(String, nullable=False)
    type = Column(String, nullable=False)  # client, fournisseur, employe
    adresse = Column(String)
    telephone = Column(String)
    email = Column(String)
    identifiant_fiscal = Column(String)
    
    # Specific fields based on type
    # For clients
    seuil_credit = Column(Float, default=0)
    conditions_paiement = Column(String)
    categorie_client = Column(String)  # particulier, professionnel, etc.
    
    # For fournisseurs
    conditions_livraison = Column(String)
    delai_paiement = Column(Integer)  # in days
    
    # For employes
    poste = Column(String)
    date_embauche = Column(DateTime)
    statut = Column(Boolean, default=True)  # Actif/inactif
    
    # Common fields
    compagnie_id = Column(String)  # UUID of the associated company
    solde = Column(Float, default=0)