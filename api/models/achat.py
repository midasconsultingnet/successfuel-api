from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from enum import Enum as PyEnum
from .base_model import BaseModel
from sqlalchemy.orm import relationship


class StatutCommande(PyEnum):
    EN_ATTENTE = "en_attente"
    CONFIRMEE = "confirme"
    ANNULEE = "annule"
    PARTIELLEMENT_LIVREE = "partiellement_livre"
    LIVREE = "livre"
    FACTUREE = "facture"


class Achat(BaseModel):
    __tablename__ = "achats"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fournisseur_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    station_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the station
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
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the company

    # Nouveaux champs requis
    config_produit = Column(String)  # JSON string pour les configurations du produit
    regles_stock = Column(String)  # JSON string pour les règles de stock
    date_livraison_prevue = Column(DateTime)
    statut_commande = Column(String, default=StatutCommande.EN_ATTENTE.value)
    date_validation = Column(DateTime)  # Date de validation de la commande

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