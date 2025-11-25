from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.schema import CheckConstraint
from database.database import Base
from datetime import datetime
import uuid

class TentativeConnexion(Base):
    __tablename__ = "tentatives_connexion"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(50), nullable=False)
    ip_connexion = Column(String(45))
    resultat_connexion = Column(String(10), CheckConstraint("resultat_connexion IN ('Reussie', 'Echouee')"))
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class EvenementSecurite(Base):
    __tablename__ = "evenements_securite"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_evenement = Column(String(50), nullable=False)  # 'connexion_anormale', 'tentative_acces_non_autorise', etc.
    description = Column(Text)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    ip_utilisateur = Column(String(45))
    poste_utilisateur = Column(String(100))
    session_id = Column(String(100))
    donnees_supplementaires = Column(JSONB)
    statut = Column(String(20), CheckConstraint("statut IN ('NonTraite', 'EnCours', 'Traite', 'Ferme')"), default='NonTraite')
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ModificationSensible(Base):
    __tablename__ = "modifications_sensibles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    type_operation = Column(String(50), nullable=False)  # 'modification_vente', 'annulation_vente', 'modification_stock', etc.
    objet_modifie = Column(String(50), nullable=False)  # 'vente', 'stock', 'achat', etc.
    objet_id = Column(PG_UUID(as_uuid=True))
    ancienne_valeur = Column(JSONB)
    nouvelle_valeur = Column(JSONB)
    seuil_alerte = Column(Boolean, default=False)  # TRUE si dépasse un seuil défini
    commentaire = Column(Text)
    ip_utilisateur = Column(String(45))
    poste_utilisateur = Column(String(100))
    statut = Column(String(20), CheckConstraint("statut IN ('Enregistre', 'Enquete', 'Traite', 'Ferme')"), default='Enregistre')
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class PermissionTresorerie(Base):
    __tablename__ = "permissions_tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    tresorerie_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresoreries.id"))
    droits = Column(String(20), CheckConstraint("droits IN ('lecture', 'ecriture', 'validation', 'admin')"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_hash = Column(String(255), nullable=False)  # Selon la table dans le schéma
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)