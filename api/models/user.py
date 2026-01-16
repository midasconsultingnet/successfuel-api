from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from .base_model import BaseModel


class NiveauValidation(PyEnum):
    NIVEAU_1 = 1
    NIVEAU_2 = 2
    NIVEAU_3 = 3
    NIVEAU_4 = 4
    NIVEAU_5 = 5


class User(BaseModel):
    __tablename__ = "utilisateur"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    login = Column(String(255), unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # gerant_compagnie, utilisateur_compagnie
    date_derniere_connexion = Column(DateTime)
    actif = Column(Boolean, default=True)
    compagnie_id = Column(UUID(as_uuid=True))  # Changed to proper UUID type
    # niveau_validation = Column(Enum(NiveauValidation), nullable=True)  # Temporairement désactivé car la colonne n'existe pas dans la base de données

    # Relations
    demandes_achat = relationship("DemandeAchat", back_populates="utilisateur", lazy="select")
    validations_demande = relationship("ValidationDemande", back_populates="utilisateur", lazy="select")
    regles_validation = relationship("RegleValidation", back_populates="utilisateur_valideur", lazy="select")
    ecritures_comptables = relationship("EcritureComptableModel", back_populates="utilisateur", lazy="select")

