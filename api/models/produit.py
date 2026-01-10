from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from .base_model import BaseModel

class FamilleProduit(BaseModel):
    __tablename__ = "famille_produit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    description = Column(String)
    code = Column(String, nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)  # Added company_id
    famille_parente_id = Column(UUID(as_uuid=True), ForeignKey("famille_produit.id"))  # For hierarchical families

    # Relation avec la famille parente et les sous-familles
    famille_parente = relationship("FamilleProduit", remote_side=[id], back_populates="sous_familles")
    sous_familles = relationship("FamilleProduit", back_populates="famille_parente")

class Produit(BaseModel):
    __tablename__ = "produit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    code = Column(String, nullable=False)
    code_barre = Column(String, nullable=True)  # Code-barres du produit, NULL autorisé
    description = Column(String)
    unite_mesure = Column(String, default="unité")  # litre, unité, kg, etc.
    type = Column(String, nullable=False)  # boutique, carburant, lubrifiant, gaz, service
    famille_id = Column(UUID(as_uuid=True), ForeignKey("famille_produit.id"))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnie.id"))  # UUID of the company (for products associated with a specific company)
    has_stock = Column(Boolean, default=True)  # True for products with stock (boutique, lubrifiants, gaz), False for services

    # Unique constraints: both code and code_barre must be unique per company
    __table_args__ = (
        UniqueConstraint('code', 'compagnie_id', name='uq_code_compagnie'),
        UniqueConstraint('code_barre', 'compagnie_id', name='uq_code_barre_compagnie'),
    )

    # Relationships
    stocks = relationship("StockProduit", back_populates="produit")
    lots = relationship("Lot", back_populates="produit")
    achats_details = relationship("AchatDetail", back_populates="produit")
    lignes_demande_achat = relationship("LigneDemandeAchat", back_populates="produit")
