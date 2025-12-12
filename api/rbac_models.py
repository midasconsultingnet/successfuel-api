from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .models.base import Base
from datetime import datetime
import uuid

class Profil(Base):
    __tablename__ = 'profils'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    description = Column(Text)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey('compagnie.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relation avec les modules (lazy loading to prevent circular references in Pydantic serialization)
    modules = relationship("ProfilModule", back_populates="profil", lazy="select")
    utilisateurs = relationship("UtilisateurProfil", back_populates="profil", lazy="select")

    __table_args__ = (UniqueConstraint('compagnie_id', 'nom', name='uq_profil_par_compagnie'),)

class ProfilModule(Base):
    __tablename__ = 'profil_module'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profil_id = Column(UUID(as_uuid=True), ForeignKey('profils.id'), nullable=False)
    module_nom = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())

    profil = relationship("Profil", back_populates="modules", lazy="select")

    __table_args__ = (
        UniqueConstraint('profil_id', 'module_nom', name='uq_profil_module'),
        CheckConstraint(
            module_nom.in_([
                'Module Utilisateurs et Authentification',
                'Module Structure de la Compagnie',
                'Module Tiers',
                'Module Produits et Stocks Complet',
                'Module Trésoreries',
                'Module Achats Carburant',
                'Module Achats Boutique',
                'Module Ventes Carburant',
                'Module Ventes Boutique',
                'Module Livraisons Carburant',
                'Module Inventaires Carburant',
                'Module Inventaires Boutique',
                'Module Mouvements Financiers',
                'Module Salaires et Rémunérations',
                'Module Charges de Fonctionnement',
                'Module Immobilisations',
                'Module États, Bilans et Comptabilité'
            ]),
            name='check_module_nom'
        )
    )

class UtilisateurProfil(Base):
    __tablename__ = 'utilisateur_profil'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    profil_id = Column(UUID(as_uuid=True), ForeignKey('profils.id'), nullable=False)
    date_affectation = Column(DateTime, default=func.now())
    utilisateur_affectation_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)

    profil = relationship("Profil", back_populates="utilisateurs", lazy="select")

    __table_args__ = (UniqueConstraint('utilisateur_id', name='uq_utilisateur_profil'),)