from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from decimal import Decimal
import uuid
from .base_model import BaseModel
from sqlalchemy.orm import relationship


class Achat(BaseModel):
    __tablename__ = "achats"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fournisseur_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    station_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the station
    tresorerie_id = Column(PG_UUID(as_uuid=True))  # ID of the treasury (either station or global treasury)
    date = Column(DateTime, nullable=False)
    informations = Column(JSONB)  # JSONB field to store additional information like numero_bl, numero_facture, etc.
    montant_total = Column(String, nullable=False)  # Using String to represent DECIMAL
    statut = Column(String, default="brouillon")  # brouillon, valide, facture, paye
    type_paiement = Column(String)  # prepaye, cod, differe, consignation, mixte
    delai_paiement = Column(Integer)  # in days
    mode_reglement = Column(String)  # cash, cheque, virement, mobile_money
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the company
    date_livraison_prevue = Column(DateTime)

    # Relations
    details = relationship("AchatDetail", back_populates="achat")


class AchatDetail(BaseModel):
    __tablename__ = "achats_details"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_id = Column(PG_UUID(as_uuid=True), ForeignKey("achats.id"), nullable=False)
    produit_id = Column(PG_UUID(as_uuid=True), ForeignKey("produit.id"), nullable=False)
    quantite_demandee = Column(Integer, nullable=False)
    quantite_recue = Column(Integer, default=0)
    quantite_facturee = Column(Integer, default=0)
    prix_unitaire_demande = Column(Float, nullable=False)
    prix_unitaire_recu = Column(Float)  # Updated when received
    prix_unitaire_facture = Column(Float)  # Updated when invoiced
    montant = Column(Float, nullable=False)
    taux_ecart = Column(Float, default=0.0)  # Pourcentage d'écart entre prix unitaire demandé et reçu

    # Relations
    achat = relationship("Achat", back_populates="details")
    produit = relationship("Produit", back_populates="achats_details")