from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .base import Base
from sqlalchemy.orm import relationship

class Tiers(Base):
    __tablename__ = "tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    type = Column(String, nullable=False)  # client, fournisseur, employe
    adresse = Column(String)
    telephone = Column(String)
    email = Column(String)
    identifiant_fiscal = Column(String)

    # Specific fields based on type
    # For clients
    seuil_credit = Column(DECIMAL(15, 2), default=0)
    conditions_paiement = Column(String)
    categorie_client = Column(String)  # particulier, professionnel, etc.

    # For fournisseurs
    conditions_livraison = Column(String)
    delai_paiement = Column(Integer)  # in days

    # For employes
    poste = Column(String)
    date_embauche = Column(DateTime)
    # Modification du champ statut pour gérer actif/inactif/supprimé
    statut = Column(String(20), default='inactif')  # 'actif', 'inactif', 'supprimé'

    # Common fields
    compagnie_id = Column(UUID(as_uuid=True))  # UUID of the associated company
    # Champ solde supprimé pour éviter la redondance
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=datetime.utcnow())

    # Relations avec les autres tables
    soldes = relationship("SoldeTiers", back_populates="tiers", uselist=False, cascade="all, delete-orphan")
    mouvements = relationship("MouvementTiers", back_populates="tiers")

class SoldeTiers(Base):
    __tablename__ = "solde_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), unique=True, nullable=False)
    montant_initial = Column(DECIMAL(15, 2), nullable=False)
    montant_actuel = Column(DECIMAL(15, 2), default=0)
    devise = Column(String, default='XOF')
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

    # Relation avec le tiers
    tiers = relationship("Tiers", back_populates="soldes")

class MouvementTiers(Base):
    __tablename__ = "mouvement_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    type_mouvement = Column(String, nullable=False)  # 'débit' ou 'crédit'
    montant = Column(DECIMAL(15, 2), nullable=False)
    date_mouvement = Column(DateTime, nullable=False)
    description = Column(String)
    module_origine = Column(String, nullable=False)  # Module d'origine de la transaction
    reference_origine = Column(String, nullable=False)  # Référence de l'opération originale
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    numero_piece_comptable = Column(String)
    statut = Column(String, default='validé')  # 'validé', 'annulé'

    # Relations
    tiers = relationship("Tiers", back_populates="mouvements")