from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base
from datetime import datetime
import uuid

class Vente(Base):
    __tablename__ = "ventes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    date_vente = Column(Date, nullable=False)
    total_ht = Column(Numeric(18,2), nullable=False)
    total_ttc = Column(Numeric(18,2), nullable=False)
    total_tva = Column(Numeric(18,2), nullable=False)
    reference_facture = Column(String(100))
    observation = Column(Text)
    type_vente = Column(String(20), default='Boutique')
    type_transaction = Column(String(20), default='General')
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    devise_code = Column(String(3), default='MGA')
    taux_change = Column(Numeric(15,6), default=1.000000)
    journal_entry_id = Column(UUID(as_uuid=True))
    statut = Column(String(20), default='Valide')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class VenteDetail(Base):
    __tablename__ = "ventes_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vente_id = Column(UUID(as_uuid=True), ForeignKey("ventes.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    pistolet_id = Column(UUID(as_uuid=True), ForeignKey("pistolets.id"))
    index_debut = Column(Numeric(18,3))
    index_fin = Column(Numeric(18,3))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire_ht = Column(Numeric(18,4), nullable=False)
    prix_unitaire_ttc = Column(Numeric(18,4), nullable=False)
    taux_tva = Column(Numeric(5,2), default=0)
    # Les champs montant_ht, montant_tva, et montant_ttc sont calculés dans la base de données
    taxes_detaillees = Column(JSONB, default={})
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Reglement(Base):
    __tablename__ = "reglements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    date_reglement = Column(Date, nullable=False)
    montant = Column(Numeric(18,2), nullable=False)
    type_paiement = Column(String(50), nullable=False)
    reference_paiement = Column(String(100))
    observation = Column(Text)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    statut = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)