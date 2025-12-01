from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey, CheckConstraint
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
    type_achat = Column(String(20), default='Produits', nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    devise_code = Column(String(3), default='MGA')
    taux_change = Column(Numeric(15,6), default=1.000000)
    journal_entry_id = Column(UUID(as_uuid=True))
    statut = Column(String(40), default='En attente de livraison', nullable=False)
    date_livraison = Column(Date)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("total >= 0", name="achats_total_check"),
        CheckConstraint("statut IN ('En attente de livraison', 'Livré', 'Annulé')", name="achats_statut_check"),
        CheckConstraint("type_achat IN ('Produits', 'Carburants')", name="achats_type_achat_check"),
    )

class AchatDetail(Base):
    __tablename__ = "achats_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_id = Column(UUID(as_uuid=True), ForeignKey("achats.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"))
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), nullable=False)
    statut = Column(String(20), default='Actif', nullable=False)
    # Le champ montant est généré automatiquement dans la base de données comme (quantite * prix_unitaire)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("prix_unitaire >= 0", name="achats_details_prix_unitaire_check"),
        CheckConstraint("quantite >= 0", name="achats_details_quantite_check"),
        CheckConstraint("statut IN ('Actif', 'Inactif', 'Supprime')", name="achats_details_statut_check"),
    )

class BonCommande(Base):
    __tablename__ = "bons_commande"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_bon = Column(String(50), unique=True, nullable=False)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("fournisseurs.id"))
    date_bon = Column(Date, nullable=False)
    total = Column(Numeric(18,2), nullable=False)
    observation = Column(Text)
    type_bon = Column(String(20), default='Produits', nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    statut = Column(String(40), default='En cours', nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("total >= 0", name="bons_commande_total_check"),
        CheckConstraint("statut IN ('En cours', 'Livre', 'Facture', 'Annule')", name="bons_commande_statut_check"),
        CheckConstraint("type_bon IN ('Produits', 'Carburants')", name="bons_commande_type_bon_check"),
    )