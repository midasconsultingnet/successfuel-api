from sqlalchemy import Column, String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum as PyEnum
from ..base import Base
from .base_model import BaseModel


class NiveauValidation(PyEnum):
    NIVEAU_1 = 1
    NIVEAU_2 = 2
    NIVEAU_3 = 3
    NIVEAU_4 = 4
    NIVEAU_5 = 5


class ValidationDemande(BaseModel):
    __tablename__ = "validation_demande"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    niveau = Column(Enum(NiveauValidation), nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    utilisateur = relationship("User", back_populates="validations_demande")
    
    demande_achat_id = Column(UUID(as_uuid=True), ForeignKey('demande_achat.id'), nullable=False)
    demande_achat = relationship("DemandeAchat", back_populates="validations")
    
    statut = Column(String(20), default='en_attente')  # en_attente, approuve, rejete
    date_validation = Column(DateTime, nullable=True)
    commentaire = Column(Text, nullable=True)
    est_actif = Column(Boolean, default=True)  # Pour permettre une désactivation logique


class RegleValidation(BaseModel):
    __tablename__ = "regle_validation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey('compagnie.id'), nullable=False)
    compagnie = relationship("Compagnie", back_populates="regles_validation")
    
    seuil_montant = Column(Numeric(10, 2), nullable=True)  # Montant à partir duquel une validation est requise
    niveau_validation_requis = Column(Enum(NiveauValidation), nullable=False)
    
    utilisateur_valideur_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    utilisateur_valideur = relationship("User", back_populates="regles_validation")
    
    est_active = Column(Boolean, default=True)  # Pour permettre une désactivation logique