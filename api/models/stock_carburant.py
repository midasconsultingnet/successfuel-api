from sqlalchemy import Column, String, Integer, Boolean, DateTime, func, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel


class StockCarburant(BaseModel):
    __tablename__ = "stock_carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuve.id"), nullable=False)
    quantite_theorique = Column(DECIMAL(12, 2), nullable=False, default=0)  # in liters
    quantite_reelle = Column(DECIMAL(12, 2), nullable=False, default=0)  # in liters
    date_dernier_calcul = Column(DateTime, nullable=False, default=func.now())
    cout_moyen_pondere = Column(DECIMAL(12, 2), default=0)  # Average weighted cost
    prix_vente = Column(DECIMAL(12, 2), default=0)  # Selling price
    seuil_stock_min = Column(DECIMAL(12, 2), default=0)  # Minimum stock threshold

    # Relationships
    cuve = relationship("Cuve", back_populates="stock_carburant")