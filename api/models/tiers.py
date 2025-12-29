from sqlalchemy import Column, String, UUID, DateTime, CheckConstraint, Float, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base_model import BaseModel
import uuid


class Tiers(BaseModel):
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

    # Paramètres spécifiques pour les fournisseurs
    type_paiement = Column(String(50))  # "comptant", "crédit", "carte", etc.
    delai_paiement = Column(String(20))  # "30_jours", "60_jours", "90_jours", "sur_facture", etc.
    acompte_requis = Column(Numeric(5, 2))  # Pourcentage d'acompte requis (ex: 10.00 pour 10%)
    seuil_credit = Column(Numeric(10, 2))  # Montant maximum de crédit autorisé

    # Relations - back_populates
    soldes = relationship("SoldeTiers", back_populates="tiers", lazy="select")
    mouvements = relationship("MouvementTiers", back_populates="tiers", lazy="select")
    journaux_modifications = relationship("JournalModificationTiers", back_populates="tiers", lazy="select")
    demandes_achat = relationship("DemandeAchat", back_populates="tiers", lazy="select")


class SoldeTiers(BaseModel):
    __tablename__ = "solde_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), nullable=False)  # Lier le solde à une station
    montant_initial = Column(Float, nullable=False)
    montant_actuel = Column(Float, nullable=False)
    devise = Column(String(10), default="XOF")
    date_derniere_mise_a_jour = Column(DateTime)  # Date de la dernière mise à jour du solde

    # Relations
    tiers = relationship("Tiers", back_populates="soldes", lazy="select")


class MouvementTiers(BaseModel):
    __tablename__ = "mouvement_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # Lier le mouvement à une station
    type_mouvement = Column(String(20), CheckConstraint("type_mouvement IN ('débit', 'crédit')"), nullable=False)
    montant = Column(Float, nullable=False)
    date_mouvement = Column(DateTime, nullable=False)  # Date du mouvement
    description = Column(String(255))
    reference = Column(String(100))  # Référence de la transaction
    statut = Column(String(20), default='en_attente')  # en_attente, valide, annule
    module_origine = Column(String(100), nullable=False)  # Module d'origine du mouvement
    reference_origine = Column(String(100), nullable=False)  # Référence d'origine du mouvement
    utilisateur_id = Column(UUID(as_uuid=True), nullable=False)  # ID de l'utilisateur qui a effectué le mouvement
    est_annule = Column(Boolean, default=False)  # Pour gérer les annulations
    transaction_source_id = Column(UUID(as_uuid=True))  # ID de la transaction source (achat, vente, etc.)
    type_transaction_source = Column(String(50))  # Type de la transaction source ('achat', 'vente', etc.)

    # Relations
    tiers = relationship("Tiers", back_populates="mouvements", lazy="select")


class JournalModificationTiers(BaseModel):
    __tablename__ = "journal_modification_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), nullable=False)  # Utilisateur qui a effectué la modification
    champ_modifie = Column(String(100), nullable=False)  # Nom du champ modifié
    valeur_precedente = Column(String)  # Valeur avant la modification
    valeur_nouvelle = Column(String)  # Valeur après la modification
    type_modification = Column(String(50), nullable=False)  # 'creation', 'mise_a_jour', 'suppression'
    ip_modification = Column(String(45))  # Adresse IP de l'utilisateur
    user_agent = Column(String)  # User agent du navigateur
    donnees_completes_avant = Column(JSONB)  # Données complètes du tiers avant modification
    donnees_completes_apres = Column(JSONB)  # Données complètes du tiers après modification

    # Relations
    tiers = relationship("Tiers", back_populates="journaux_modifications", lazy="select")