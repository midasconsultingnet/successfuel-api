from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel


class AffectationUtilisateurStation(BaseModel):
    __tablename__ = "affectation_utilisateur_station"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    station_id = Column(String, nullable=False)  # UUID of the station
    date_affectation = Column(DateTime(timezone=True), default=func.now(), nullable=False)