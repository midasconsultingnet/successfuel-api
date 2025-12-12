from sqlalchemy import Column, String, UUID, DateTime, CheckConstraint, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Tiers(Base):
    __tablename__ = "tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compagnie_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(String(50), CheckConstraint("type IN ('client', 'fournisseur', 'employé')"), nullable=False)
    nom = Column(String(255), nullable=False)
    email = Column(String(255))
    telephone = Column(String(50))
    adresse = Column(String)  # Utilisation de String au lieu de TEXT pour plus de souplesse
    statut = Column(String(20), default='actif')
    donnees_personnelles = Column(JSONB)  # Informations spécifiques selon le type
    station_ids = Column(JSONB, default='[]')  # IDs des stations associées
    metadonnees = Column(JSONB)  # Pour stocker des infos additionnelles
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations - back_populates
    soldes = relationship("SoldeTiers", back_populates="tiers")
    mouvements = relationship("MouvementTiers", back_populates="tiers")


class SoldeTiers(Base):
    __tablename__ = "solde_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # Lier le solde à une station
    solde_actuel = Column(Float, default=0.0)
    devise = Column(String(10), default="XOF")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    tiers = relationship("Tiers", back_populates="soldes")


class MouvementTiers(Base):
    __tablename__ = "mouvement_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # Lier le mouvement à une station
    type_mouvement = Column(String(20), CheckConstraint("type_mouvement IN ('entree', 'sortie')"), nullable=False)
    montant = Column(Float, nullable=False)
    description = Column(String(255))
    reference = Column(String(100))  # Référence de la transaction
    statut = Column(String(20), default='en_attente')  # en_attente, valide, annule
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    tiers = relationship("Tiers", back_populates="mouvements")