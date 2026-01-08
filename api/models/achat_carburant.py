from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL, func, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import Optional
from .base_model import BaseModel

from sqlalchemy.orm import relationship

class AchatCarburant(BaseModel):
    __tablename__ = "achat_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    date_achat = Column(DateTime(timezone=True), nullable=False)
    autres_infos = Column(JSON, nullable=True)  # Anciennement numero_bl
    numero_facture = Column(String, nullable=True)
    montant_total = Column(DECIMAL(15, 2), nullable=False)
    statut = Column(String, default="brouillon")  # "brouillon", "validé", "livré", "annulé"
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)  # Anciennement station_id
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)

    # New fields for the three-stage process
    date_validation = Column(DateTime(timezone=True), nullable=True)  # Date when payment is recorded
    date_livraison = Column(DateTime(timezone=True), nullable=True)  # Date when delivery is recorded
    montant_reel = Column(DECIMAL(15, 2), nullable=True)  # Actual amount based on delivery
    ecart_achat_livraison = Column(DECIMAL(15, 2), nullable=True)  # Difference between purchase and delivery

    # Relations
    ligne_achat_carburant = relationship("LigneAchatCarburant", back_populates="achat_carburant")
    paiements = relationship("PaiementAchatCarburant", back_populates="achat_carburant")
    compensations = relationship("CompensationFinanciere", back_populates="achat_carburant")

    @property
    def quantite_theorique(self) -> Optional[float]:
        """Retourne la quantité théorique à partir de la première compensation financière."""
        if self.compensations:
            return float(self.compensations[0].quantite_theorique)
        return None

    @property
    def quantite_reelle(self) -> Optional[float]:
        """Retourne la quantité réelle à partir de la première compensation financière."""
        if self.compensations:
            return float(self.compensations[0].quantite_reelle)
        return None

class LigneAchatCarburant(BaseModel):
    __tablename__ = "ligne_achat_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_carburant_id = Column(UUID(as_uuid=True), ForeignKey("achat_carburant.id"), nullable=False)
    carburant_id = Column(UUID(as_uuid=True), ForeignKey("carburant.id"), nullable=False)  # References the carburant table
    quantite = Column(DECIMAL(12, 2), nullable=False)
    prix_unitaire = Column(DECIMAL(15, 2), nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # Anciennement cuve_id

    # Relations
    achat_carburant = relationship("AchatCarburant", back_populates="ligne_achat_carburant")

class CompensationFinanciere(BaseModel):
    __tablename__ = "compensation_financiere"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_carburant_id = Column(UUID(as_uuid=True), ForeignKey("achat_carburant.id"), nullable=False)
    type_compensation = Column(String, nullable=False)  # "avoir_reçu", "avoir_dû"
    quantite_theorique = Column(DECIMAL(12, 2), nullable=False)
    quantite_reelle = Column(DECIMAL(12, 2), nullable=False)
    difference = Column(DECIMAL(12, 2), nullable=False)
    montant_compensation = Column(DECIMAL(15, 2), nullable=False)
    motif = Column(String)
    statut = Column(String, default="émis")  # "émis", "utilisé", "partiellement_utilisé", "expiré"
    date_emission = Column(DateTime(timezone=True), default=func.now())
    date_expiration = Column(DateTime(timezone=True))

    # Relations
    achat_carburant = relationship("AchatCarburant", back_populates="compensations")

class AvoirCompensation(BaseModel):
    __tablename__ = "avoir_compensation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compensation_financiere_id = Column(UUID(as_uuid=True), ForeignKey("compensation_financiere.id"), nullable=False)
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    date_emission = Column(DateTime(timezone=True), nullable=False)
    date_utilisation = Column(DateTime(timezone=True))
    statut = Column(String, default="émis")  # "émis", "utilisé", "partiellement_utilisé", "expiré"
    utilisateur_emission_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    utilisateur_utilisation_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

class PaiementAchatCarburant(BaseModel):
    __tablename__ = "paiement_achat_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achat_carburant_id = Column(UUID(as_uuid=True), ForeignKey("achat_carburant.id"), nullable=False)
    date_paiement = Column(DateTime(timezone=True), nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    mode_paiement = Column(String, nullable=False)  # "espèces", "chèque", "virement", "carte_bancaire", etc.
    tresorerie_station_id = Column(UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    statut = Column(String, default="enregistré")  # "enregistré", "validé", "annulé"

    # Relations
    achat_carburant = relationship("AchatCarburant", back_populates="paiements")
    tresorerie_station = relationship("TresorerieStation", back_populates="paiements_achat_carburant")