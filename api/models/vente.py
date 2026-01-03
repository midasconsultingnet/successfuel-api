from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from .base_model import BaseModel
import uuid

class Vente(BaseModel):
    __tablename__ = "ventes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(PG_UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # UUID of the station
    client_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"))  # Optional - for credit sales
    date = Column(DateTime, nullable=False)
    montant_total = Column(Float, nullable=False)
    statut = Column(String, default="en_cours")  # en_cours, terminee, annulee
    type_vente = Column(String, default="produit")  # produit, service, hybride
    informations = Column(String)  # JSONB field for additional information
    tresorerie_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie.id"))  # Direct reference to tresorerie
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the company
    est_en_arret_compte = Column(Boolean, default=False)  # Flag to indicate if this sale is under account stop

    # Relationships
    details = relationship("VenteDetail", back_populates="vente", lazy="select")
    avoirs = relationship("AvoirVente", back_populates="vente", lazy="select")
    station = relationship("Station", lazy="select")
    client = relationship("Tiers", lazy="select")
    tresorerie = relationship("Tresorerie", lazy="select")

    __table_args__ = (
        Index('idx_ventes_station_id', 'station_id'),
        Index('idx_ventes_compagnie_id', 'compagnie_id'),
        Index('idx_ventes_client_id', 'client_id'),
        Index('idx_ventes_tresorerie_id', 'tresorerie_id'),
        Index('idx_ventes_statut', 'statut'),
        Index('idx_ventes_date', 'date'),
    )

class VenteDetail(BaseModel):
    __tablename__ = "ventes_details"

    vente_id = Column(PG_UUID(as_uuid=True), ForeignKey("ventes.id"), nullable=False)
    produit_id = Column(PG_UUID(as_uuid=True), ForeignKey("produit.id"), nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant = Column(Float, nullable=False)
    remise = Column(Float, default=0)

    # Relationships
    vente = relationship("Vente", back_populates="details", lazy="select")
    produit = relationship("Produit", lazy="select")

    __table_args__ = (
        Index('idx_ventes_details_vente_id', 'vente_id'),
        Index('idx_ventes_details_produit_id', 'produit_id'),
    )


class AvoirVente(BaseModel):
    __tablename__ = "avoirs_ventes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vente_id = Column(PG_UUID(as_uuid=True), ForeignKey("ventes.id"), nullable=False)  # Original sale
    numero_avoir = Column(String, nullable=False)  # Avoir number
    date_avoir = Column(DateTime, nullable=False)  # Date of the avoir
    montant_avoir = Column(Float, nullable=False)  # Total amount of the avoir
    montant_rembourse = Column(Float, default=0)  # Amount already refunded
    motif = Column(String, nullable=False)  # Reason for the avoir
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # User who created the avoir
    statut = Column(String, default="emis")  # emis, partiellement_rembourse, rembourse, annule
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # Company ID

    # Relationships
    vente = relationship("Vente", back_populates="avoirs", lazy="select")
    utilisateur = relationship("User", lazy="select")
    details = relationship("AvoirVenteDetail", back_populates="avoir_vente", lazy="select")

    __table_args__ = (
        Index('idx_avoirs_ventes_vente_id', 'vente_id'),
        Index('idx_avoirs_ventes_date_avoir', 'date_avoir'),
        Index('idx_avoirs_ventes_statut', 'statut'),
        Index('idx_avoirs_ventes_utilisateur_id', 'utilisateur_id'),
        Index('idx_avoirs_ventes_compagnie_id', 'compagnie_id'),
    )


class AvoirVenteDetail(BaseModel):
    __tablename__ = "avoirs_ventes_details"

    avoir_vente_id = Column(PG_UUID(as_uuid=True), ForeignKey("avoirs_ventes.id"), nullable=False)
    produit_id = Column(PG_UUID(as_uuid=True), ForeignKey("produit.id"), nullable=False)
    quantite = Column(Integer, nullable=False)  # Quantity returned
    prix_unitaire = Column(Float, nullable=False)  # Price at the time of original sale
    montant = Column(Float, nullable=False)  # Total amount for this item
    remise = Column(Float, default=0)  # Discount for this item

    # Relationships
    avoir_vente = relationship("AvoirVente", back_populates="details", lazy="select")
    produit = relationship("Produit", lazy="select")

    __table_args__ = (
        Index('idx_avoirs_ventes_details_avoir_vente_id', 'avoir_vente_id'),
        Index('idx_avoirs_ventes_details_produit_id', 'produit_id'),
    )


class Promotion(BaseModel):
    __tablename__ = "promotions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)  # Unique code for the promotion
    libelle = Column(String, nullable=False)  # Descriptive name of the promotion
    description = Column(String)
    type_promotion = Column(String, nullable=False)  # "reduction_pourcentage", "reduction_fixe", "produit_offert", "2eme_achat_reduit"
    valeur_promotion = Column(Float, nullable=False)  # Value of the promotion (percentage or fixed amount)
    borne_inferieure = Column(Float)  # Minimum amount to qualify for the promotion
    borne_superieure = Column(Float)  # Maximum amount for which the promotion applies
    date_debut = Column(DateTime, nullable=False)  # Start date of the promotion
    date_fin = Column(DateTime, nullable=False)  # End date of the promotion
    est_active = Column(Boolean, default=True)  # Whether the promotion is currently active
    produit_id = Column(PG_UUID(as_uuid=True), ForeignKey("produit.id"))  # Product for which the promotion applies
    produit_offert_id = Column(PG_UUID(as_uuid=True), ForeignKey("produit.id"))  # Product offered (for "produit_offert" type)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # User who created the promotion
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # Company ID

    # Relationships
    utilisateur = relationship("User", lazy="select")
    produit = relationship("Produit", foreign_keys=[produit_id], lazy="select")
    produit_offert = relationship("Produit", foreign_keys=[produit_offert_id], lazy="select")

    __table_args__ = (
        Index('idx_promotions_produit_id', 'produit_id'),
        Index('idx_promotions_utilisateur_id', 'utilisateur_id'),
        Index('idx_promotions_compagnie_id', 'compagnie_id'),
        Index('idx_promotions_est_active', 'est_active'),
        Index('idx_promotions_date_debut', 'date_debut'),
        Index('idx_promotions_date_fin', 'date_fin'),
    )
