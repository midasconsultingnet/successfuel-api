from sqlalchemy import Column, String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from enum import Enum as PyEnum
from ..base import Base
from .base_model import BaseModel


class StatutDemande(PyEnum):
    EN_ATTENTE = "en_attente"
    APPROUVEE = "approuvee"
    REJETEE = "rejetee"


class DemandeAchat(BaseModel):
    __tablename__ = "demande_achat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    objet = Column(Text, nullable=False)
    statut = Column(Enum(StatutDemande), default=StatutDemande.EN_ATTENTE, nullable=False)
    date_demande = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    date_validation = Column(DateTime, nullable=True)
    montant_total = Column(Numeric(10, 2), default=0.00)

    # Relations
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    utilisateur = relationship("User", back_populates="demandes_achat")

    tiers_id = Column(UUID(as_uuid=True), ForeignKey('tiers.id'), nullable=False)
    tiers = relationship("Tiers", back_populates="demandes_achat")

    lignes_demande = relationship("LigneDemandeAchat", back_populates="demande_achat", cascade="all, delete-orphan")
    validations = relationship("ValidationDemande", back_populates="demande_achat")


class LigneDemandeAchat(BaseModel):
    __tablename__ = "ligne_demande_achat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    designation = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Numeric(10, 2), nullable=False)
    unite = Column(String(20), default='unité')
    montant_total = Column(Numeric(10, 2), nullable=False)
    
    # Relations
    demande_achat_id = Column(UUID(as_uuid=True), ForeignKey('demande_achat.id'), nullable=False)
    demande_achat = relationship("DemandeAchat", back_populates="lignes_demande")
    
    produit_id = Column(UUID(as_uuid=True), ForeignKey('produit.id'), nullable=True)
    produit = relationship("Produit", back_populates="lignes_demande_achat")