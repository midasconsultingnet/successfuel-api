from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base_model import BaseModel
from datetime import datetime
import uuid

class MethodePaiement(BaseModel):
    __tablename__ = "methode_paiement"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)  # ex: "Espèces", "Chèque", "Virement", "Mobile Money", etc.
    description = Column(String)
    type_paiement = Column(String, nullable=False)  # cash, cheque, virement, mobile_money, etc.
    actif = Column(Boolean, default=True)
    trésorerie_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie.id"))  # Lier à une trésorerie spécifique

# Table de liaison pour permettre l'association plusieurs-à-plusieurs entre trésoreries et méthodes de paiement
class TresorerieMethodePaiement(BaseModel):
    __tablename__ = "tresorerie_methode_paiement"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trésorerie_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie.id"), nullable=False)
    methode_paiement_id = Column(PG_UUID(as_uuid=True), ForeignKey("methode_paiement.id"), nullable=False)
    actif = Column(Boolean, default=True)
