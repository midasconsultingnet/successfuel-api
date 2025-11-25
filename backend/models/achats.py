from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base
from datetime import datetime
import uuid

class Achat(Base):
    __tablename__ = "achats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("fournisseurs.id"))
    date_achat = Column(Date, nullable=False)
    total = Column(Numeric(18,2), nullable=False)
    reference_facture = Column(String(100))
    observation = Column(Text)
    type_achat = Column(String(20), default='Produits')
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    devise_code = Column(String(3), default='MGA')
    taux_change = Column(Numeric(15,6), default=1.000000)
    journal_entry_id = Column(UUID(as_uuid=True))
    statut = Column(String(40), default='En attente de livraison')
    date_livraison = Column(Date)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AchatDetail(Base):
    __tablename__ = "achats_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_id = Column(UUID(as_uuid=True), ForeignKey("achats.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), nullable=False)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class BonCommande(Base):
    __tablename__ = "bons_commande"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_bon = Column(String(50), unique=True, nullable=False)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("fournisseurs.id"))
    date_bon = Column(Date, nullable=False)
    total = Column(Numeric(18,2), nullable=False)
    observation = Column(Text)
    type_bon = Column(String(20), default='Produits')
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    statut = Column(String(40), default='En cours')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)