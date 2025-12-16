from sqlalchemy import Column, String, UUID, DateTime, CheckConstraint, Float, ForeignKey, DECIMAL, Boolean, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .base_model import BaseModel
import uuid


class BilanInitialDepart(BaseModel):
    __tablename__ = "bilan_initial_depart"

    compagnie_id = Column(UUID(as_uuid=True), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"))
    date_bilan = Column(Date, nullable=False)
    actif_immobilise = Column(DECIMAL(15,2), nullable=False)
    actif_circulant = Column(DECIMAL(15,2), nullable=False)
    total_actif = Column(DECIMAL(15,2))
    capitaux_propres = Column(DECIMAL(15,2), nullable=False)
    dettes = Column(DECIMAL(15,2), nullable=False)
    provisions = Column(DECIMAL(15,2), nullable=False)
    total_passif = Column(DECIMAL(15,2))
    utilisateur_generation_id = Column(UUID(as_uuid=True), nullable=False)
    date_generation = Column(DateTime(timezone=True), nullable=False)
    est_valide = Column(Boolean, default=False)