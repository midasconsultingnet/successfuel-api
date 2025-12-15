from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class StockProduit(BaseModel):
    __tablename__ = "stock_produit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produit_id = Column(UUID(as_uuid=True), ForeignKey("produit.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    quantite_theorique = Column(DECIMAL(12, 2), default=0)  # Quantité théorique en stock
    quantite_reelle = Column(DECIMAL(12, 2), default=0)    # Quantité réelle en stock
    date_dernier_calcul = Column(DateTime)                 # Date du dernier calcul
    cout_moyen_pondere = Column(DECIMAL(15, 2), default=0) # Coût moyen pondéré

    __table_args__ = (
        # Ajout d'une contrainte pour s'assurer qu'il n'y a qu'un seul stock par produit par station
        # Cela remplace la contrainte unique sur produit_id seule
        UniqueConstraint('produit_id', 'station_id', name='uq_produit_station'),
    )
