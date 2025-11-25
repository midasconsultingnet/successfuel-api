from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base
from datetime import datetime
import uuid

class MouvementStock(Base):
    __tablename__ = "mouvements_stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    type_mouvement = Column(String(20), nullable=False)  # 'Entree', 'Sortie', 'Transfert', 'Ajustement'
    article_id = Column(UUID(as_uuid=True), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("fournisseurs.id"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    date_mouvement = Column(Date, nullable=False)
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), default=0)
    valeur_totale = Column(Numeric(18,2), default=0)
    observation = Column(Text)
    reference_externe = Column(String(100))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MouvementStockDetail(Base):
    __tablename__ = "mouvements_stock_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mouvement_id = Column(UUID(as_uuid=True), ForeignKey("mouvements_stock.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), default=0)
    valeur_totale = Column(Numeric(18,2), default=0)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Inventaire(Base):
    __tablename__ = "inventaire"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    date_inventaire = Column(Date, nullable=False)
    heure_debut = Column(Time, nullable=False)
    heure_fin = Column(Time)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    type_inventaire = Column(String(20), default='Complet')  # 'Complet', 'Partiel', 'Spécial'
    observation = Column(Text)
    statut = Column(String(20), default='En cours')  # 'En cours', 'Terminé', 'Annulé'
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class InventaireDetail(Base):
    __tablename__ = "inventaire_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventaire_id = Column(UUID(as_uuid=True), ForeignKey("inventaire.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    stock_theorique = Column(Numeric(18,3), default=0)
    stock_reel = Column(Numeric(18,3), default=0)
    ecart = Column(Numeric(18,3), default=0)
    observation = Column(Text)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class TransfertStock(Base):
    __tablename__ = "transfert_stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    date_transfert = Column(Date, nullable=False)
    heure_transfert = Column(Time, nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    station_origine_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    station_destination_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    observation = Column(Text)
    statut = Column(String(20), default='En cours')  # 'En cours', 'Terminé', 'Annulé'
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class TransfertStockDetail(Base):
    __tablename__ = "transfert_stock_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transfert_id = Column(UUID(as_uuid=True), ForeignKey("transfert_stock.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    cuve_origine_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    cuve_destination_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), default=0)
    valeur_totale = Column(Numeric(18,2), default=0)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)