from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base_model import BaseModel
import uuid

class Vente(BaseModel):
    __tablename__ = "ventes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(PG_UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)  # UUID of the station
    client_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"))  # Optional - for credit sales
    date = Column(DateTime, nullable=False)
    montant_total = Column(Float, nullable=False)
    statut = Column(String, default="en_cours")  # en_cours, terminee, annulee
    type_vente = Column(String, default="produit")  # produit, service, hybride
    trésorerie_station_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"))  # ID of the cash register used (now referencing the new structure)
    numero_piece_comptable = Column(String)
    compagnie_id = Column(PG_UUID(as_uuid=True), nullable=False)  # UUID of the company

class VenteDetail(BaseModel):
    __tablename__ = "ventes_details"

    vente_id = Column(PG_UUID(as_uuid=True), ForeignKey("ventes.id"), nullable=False)
    produit_id = Column(PG_UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant = Column(Float, nullable=False)
    remise = Column(Float, default=0)
