from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class AchatCarburant(Base):
    __tablename__ = "achat_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    date_achat = Column(DateTime, nullable=False)
    numero_bl = Column(String, nullable=False)
    numero_facture = Column(String, nullable=False)
    montant_total = Column(DECIMAL(15, 2), nullable=False)
    statut = Column(String, default="brouillon")  # "brouillon", "validé", "facturé", "annulé"
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)

class LigneAchatCarburant(Base):
    __tablename__ = "ligne_achat_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_carburant_id = Column(UUID(as_uuid=True), ForeignKey("achat_carburant.id"), nullable=False)
    carburant_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)  # Carburant est un produit
    quantite = Column(DECIMAL(12, 2), nullable=False)
    prix_unitaire = Column(DECIMAL(15, 2), nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)

class CompensationFinanciere(Base):
    __tablename__ = "compensation_financiere"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_carburant_id = Column(UUID(as_uuid=True), ForeignKey("achat_carburant.id"), nullable=False)
    type_compensation = Column(String, nullable=False)  # "avoir_reçu", "avoir_dû"
    quantite_theorique = Column(DECIMAL(12, 2), nullable=False)
    quantite_reelle = Column(DECIMAL(12, 2), nullable=False)
    difference = Column(DECIMAL(12, 2), nullable=False)
    montant_compensation = Column(DECIMAL(15, 2), nullable=False)
    motif = Column(String)
    statut = Column(String, default="émis")  # "émis", "utilisé", "partiellement_utilisé", "expiré"
    date_emission = Column(DateTime, default=DateTime)
    date_expiration = Column(DateTime)

class AvoirCompensation(Base):
    __tablename__ = "avoir_compensation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compensation_financiere_id = Column(UUID(as_uuid=True), ForeignKey("compensation_financiere.id"), nullable=False)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    date_emission = Column(DateTime, nullable=False)
    date_utilisation = Column(DateTime)
    statut = Column(String, default="émis")  # "émis", "utilisé", "partiellement_utilisé", "expiré"
    utilisateur_emission_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    utilisateur_utilisation_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))