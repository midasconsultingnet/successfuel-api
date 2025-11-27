from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.schema import CheckConstraint
from database.database import Base
from datetime import datetime, timedelta
import uuid


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_hash = Column(String(255), nullable=False)  # Haché du jeton
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    # Endpoint pour lequel le jeton est valide
    type_endpoint = Column(String(20), CheckConstraint("type_endpoint IN ('administrateur', 'utilisateur')"), default='utilisateur', index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class TentativeConnexion(Base):
    __tablename__ = "tentatives_connexion"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(50), nullable=False, index=True)
    ip_connexion = Column(String(45), index=True)
    resultat_connexion = Column(String(10), CheckConstraint("resultat_connexion IN ('Reussie', 'Echouee')"))
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"))  # NULL si échec
    # Endpoint utilisé pour la connexion
    type_endpoint = Column(String(20), CheckConstraint("type_endpoint IN ('administrateur', 'utilisateur')"), default='utilisateur', index=True)
    # Type de l'utilisateur
    type_utilisateur = Column(String(30), CheckConstraint("type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')"), default='utilisateur_compagnie', index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class TentativeAccesNonAutorise(Base):
    __tablename__ = "tentatives_acces_non_autorise"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"), index=True)
    # Endpoint que l'utilisateur a tenté d'accéder
    endpoint_accesse = Column(String(20), nullable=False, index=True)
    # Endpoint que l'utilisateur aurait dû utiliser
    endpoint_autorise = Column(String(20), index=True)
    ip_connexion = Column(String(45))
    statut = Column(String(20), CheckConstraint("statut IN ('EnAttente', 'Traite', 'Enquete')"), default='Traite')
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class EvenementSecurite(Base):
    __tablename__ = "evenements_securite"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Ex: 'connexion_anormale', 'tentative_acces_non_autorise', etc.
    type_evenement = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"), index=True)
    ip_utilisateur = Column(String(45))
    poste_utilisateur = Column(String(100))
    session_id = Column(String(100))
    donnees_supplementaires = Column(JSONB)
    statut = Column(String(20), CheckConstraint("statut IN ('NonTraite', 'EnCours', 'Traite', 'Ferme')"), default='NonTraite')
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class ModificationSensible(Base):
    __tablename__ = "modifications_sensibles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"), index=True)
    # Ex: 'modification_vente', 'annulation_vente', 'modification_stock', etc.
    type_operation = Column(String(50), nullable=False)
    # Ex: 'vente', 'stock', 'achat', etc.
    objet_modifie = Column(String(50), index=True)
    objet_id = Column(PG_UUID(as_uuid=True), index=True)
    ancienne_valeur = Column(JSONB)
    nouvelle_valeur = Column(JSONB)
    seuil_alerte = Column(Boolean, default=False)  # TRUE si dépasse un seuil défini
    commentaire = Column(Text)
    ip_utilisateur = Column(String(45))
    poste_utilisateur = Column(String(100))
    statut = Column(String(20), CheckConstraint("statut IN ('Enregistre', 'Enquete', 'Traite', 'Ferme')"), default='Enregistre')
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class PermissionTresorerie(Base):
    __tablename__ = "permissions_tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False, index=True)
    tresorerie_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresoreries.id"), nullable=False, index=True)
    # Ex: 'LECTURE', 'ECRITURE', 'VALIDATION', 'ADMIN'
    droits = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    # Contrainte unique pour éviter les doublons
    __table_args__ = (CheckConstraint('utilisateur_id IS NOT NULL AND tresorerie_id IS NOT NULL'),)


class PolitiqueSecurite(Base):
    __tablename__ = "politiques_securite"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_politique = Column(String(100), nullable=False)
    description = Column(Text)
    # 'mot_de_passe', 'connexion', 'acces_donnees', etc.
    type_politique = Column(String(50), nullable=False, index=True)
    valeur_parametre = Column(String(200))
    seuil_valeur = Column(Integer)
    est_actif = Column(Boolean, default=True, index=True)
    commentaire = Column(Text)
    # Utilisateur qui a configuré la politique
    utilisateur_config_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    # Référence corrigée
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)