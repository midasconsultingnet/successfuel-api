from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class FamilleProduit(Base):
    __tablename__ = "familles_produits"

    nom = Column(String, nullable=False)
    description = Column(String)
    code = Column(String, unique=True, nullable=False)
    famille_parente_id = Column(Integer, ForeignKey("familles_produits.id"))  # For hierarchical families

class Produit(Base):
    __tablename__ = "produits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    unite_mesure = Column(String, default="unité")  # litre, unité, kg, etc.
    type = Column(String, nullable=False)  # boutique, carburant, lubrifiant, gaz, service
    prix_vente = Column(Float, nullable=False)
    seuil_stock_min = Column(Float, default=0)  # For products with stock
    cout_moyen = Column(Float, default=0)  # For products with stock
    famille_id = Column(Integer, ForeignKey("familles_produits.id"))
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"))  # UUID of the station (for products associated with a specific station)
    has_stock = Column(Boolean, default=True)  # True for products with stock (boutique, lubrifiants, gaz), False for services
    date_limite_consommation = Column(DateTime)  # For products with expiry date