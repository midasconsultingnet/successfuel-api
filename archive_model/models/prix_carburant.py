from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .base import Base


class PrixCarburant(Base):
    __tablename__ = "prix_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    carburant_id = Column(UUID(as_uuid=True), ForeignKey("carburant.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    prix_achat = Column(DECIMAL(15, 2))
    prix_vente = Column(DECIMAL(15, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)