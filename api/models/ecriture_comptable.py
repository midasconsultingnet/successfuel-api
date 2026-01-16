from sqlalchemy import Column, DateTime, String, Text, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base_model import BaseModel
import uuid


class EcritureComptableModel(BaseModel):
    __tablename__ = "ecriture_comptable"

    date_ecriture = Column(DateTime(timezone=True), nullable=False)
    libelle_ecriture = Column(Text)
    compte_debit = Column(UUID(as_uuid=True), ForeignKey("plan_comptable.id"), nullable=False)
    compte_credit = Column(UUID(as_uuid=True), ForeignKey("plan_comptable.id"), nullable=False)
    montant = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(10), default='XOF')
    tiers_id = Column(UUID(as_uuid=True), ForeignKey("tiers.id"))
    module_origine = Column(String(100))
    reference_origine = Column(String(100))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)
    est_validee = Column(Boolean, default=False)

    # Relations
    tiers = relationship("Tiers", back_populates="ecritures")
    utilisateur = relationship("User", back_populates="ecritures_comptables")
    compagnie = relationship("Compagnie", back_populates="ecritures_comptables")
    compte_debit_rel = relationship("PlanComptableModel", foreign_keys=[compte_debit], back_populates="ecritures_debit")
    compte_credit_rel = relationship("PlanComptableModel", foreign_keys=[compte_credit], back_populates="ecritures_credit")