from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class Lot(Base):
    __tablename__ = "lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produit_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)
    numero_lot = Column(String, nullable=False)  # Numéro du lot
    quantite = Column(Float, nullable=False)  # Quantité dans ce lot
    date_production = Column(DateTime)  # Date de production du lot
    date_peremption = Column(DateTime)  # Date de péremption du lot
    date_creation = Column(DateTime)