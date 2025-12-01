from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base
from datetime import datetime
import uuid

class MouvementTresorerie(Base):
    __tablename__ = "mouvements_tresorerie"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    type_mouvement = Column(String(20), nullable=False)  # 'Encaissement', 'Décaissement', 'Virement'
    tresorerie_id = Column(UUID(as_uuid=True), ForeignKey("tresoreries.id"), nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    date_mouvement = Column(Date, nullable=False)
    heure_mouvement = Column(Time, nullable=False)
    montant = Column(Numeric(18,2), nullable=False)
    devise_montant = Column(String(3), default='MGA')
    taux_change = Column(Numeric(15,6), default=1.000000)
    montant_devise = Column(Numeric(18,2), default=0)
    tiers_id = Column(UUID(as_uuid=True))  # Peut être un client, fournisseur, etc.
    type_tiers = Column(String(20))  # 'Client', 'Fournisseur', 'Employe', 'Autre'
    reference_externe = Column(String(100))
    observation = Column(Text)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MouvementTresorerieDetail(Base):
    __tablename__ = "mouvements_tresorerie_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mouvement_id = Column(UUID(as_uuid=True), ForeignKey("mouvements_tresorerie.id"), nullable=False)
    compte_comptable_id = Column(UUID(as_uuid=True), ForeignKey("plan_comptable.id"))
    type_operation = Column(String(20))  # 'Debit' ou 'Credit'
    montant = Column(Numeric(18,2), nullable=False)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Journal(Base):
    __tablename__ = "journaux"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    libelle = Column(String(100), nullable=False)
    type_journal = Column(String(30), nullable=False)  # 'Ventes', 'Achats', 'Banque', 'Caisse', 'OD', etc.
    observation = Column(Text)
    statut = Column(String(20), default='Actif')
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)