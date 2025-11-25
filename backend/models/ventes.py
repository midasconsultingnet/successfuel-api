from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base
from datetime import datetime
import uuid

class Vente(Base):
    __tablename__ = "ventes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    date_vente = Column(Date, nullable=False)
    heure_vente = Column(Time, nullable=False)
    montant_total = Column(Numeric(18,2), nullable=False)
    montant_encaisse = Column(Numeric(18,2), default=0)
    montant_rendu = Column(Numeric(18,2), default=0)
    type_paiement = Column(String(50), default='Espèces')
    reference_paiement = Column(String(100))
    observation = Column(Text)
    type_vente = Column(String(20), default='Normale')  # 'Normale', 'Retour', 'Gratuite'
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    devise_code = Column(String(3), default='MGA')
    taux_change = Column(Numeric(15,6), default=1.000000)
    journal_entry_id = Column(UUID(as_uuid=True))
    statut = Column(String(20), default='Finalisée')  # 'Brouillon', 'Finalisée', 'Annulée', 'Retour'
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class VenteDetail(Base):
    __tablename__ = "ventes_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vente_id = Column(UUID(as_uuid=True), ForeignKey("ventes.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    pistolet_id = Column(UUID(as_uuid=True), ForeignKey("pistolets.id"))
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), nullable=False)
    remise = Column(Numeric(18,4), default=0)
    taux_tva = Column(Numeric(5,2), default=0)
    montant_tva = Column(Numeric(18,2), default=0)
    montant_ht = Column(Numeric(18,2), default=0)
    montant_ttc = Column(Numeric(18,2), default=0)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Reglement(Base):
    __tablename__ = "reglements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
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
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)