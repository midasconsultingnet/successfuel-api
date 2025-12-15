from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from .base_model import BaseModel

class Achat(BaseModel):
    __tablename__ = "achats"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fournisseur_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
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

class AchatDetail(BaseModel):
    __tablename__ = "achats_details"

    achat_id = Column(PG_UUID(as_uuid=True), ForeignKey("achats.id"), nullable=False)
    produit_id = Column(PG_UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)
    quantite_demandee = Column(Integer, nullable=False)
    quantite_recue = Column(Integer, default=0)
    quantite_facturee = Column(Integer, default=0)
    prix_unitaire_demande = Column(Float, nullable=False)
    prix_unitaire_recu = Column(Float)  # Updated when received
    prix_unitaire_facture = Column(Float)  # Updated when invoiced
    montant = Column(Float, nullable=False)