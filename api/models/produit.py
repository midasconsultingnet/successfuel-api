from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from .base_model import BaseModel

class FamilleProduit(BaseModel):
    __tablename__ = "famille_produit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    description = Column(String)
    code = Column(String, unique=True, nullable=False)
    famille_parente_id = Column(UUID(as_uuid=True), ForeignKey("famille_produit.id"))  # For hierarchical families

    # Relation avec la famille parente et les sous-familles
    famille_parente = relationship("FamilleProduit", remote_side=[id], back_populates="sous_familles")
    sous_familles = relationship("FamilleProduit", back_populates="famille_parente")

class Produit(BaseModel):
    __tablename__ = "produit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    unite_mesure = Column(String, default="unité")  # litre, unité, kg, etc.
    type = Column(String, nullable=False)  # boutique, carburant, lubrifiant, gaz, service
    prix_vente = Column(Float, nullable=False)
    seuil_stock_min = Column(Float, default=0)  # For products with stock
    cout_moyen = Column(Float, default=0)  # For products with stock
    famille_id = Column(UUID(as_uuid=True), ForeignKey("famille_produit.id"))
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"))  # UUID of the station (for products associated with a specific station)
    has_stock = Column(Boolean, default=True)  # True for products with stock (boutique, lubrifiants, gaz), False for services
    date_limite_consommation = Column(DateTime)  # For products with expiry date

    # Relationships
    stocks = relationship("StockProduit", back_populates="produit")
    lots = relationship("Lot", back_populates="produit")
    achats_details = relationship("AchatDetail", back_populates="produit")
    lignes_demande_achat = relationship("LigneDemandeAchat", back_populates="produit")
