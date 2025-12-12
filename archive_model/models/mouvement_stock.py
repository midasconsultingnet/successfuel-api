from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class MouvementStock(Base):
    __tablename__ = "mouvements_stock"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produit_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    type_mouvement = Column(String, nullable=False)  # "entree", "sortie", "ajustement", "inventaire"
    quantite = Column(Float, nullable=False)
    date_mouvement = Column(DateTime, nullable=False)
    description = Column(String)
    module_origine = Column(String, nullable=False)  # Module d'origine du mouvement
    reference_origine = Column(String, nullable=False)  # Référence dans le module d'origine
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)  # Utilisateur qui a effectué le mouvement
    cout_unitaire = Column(DECIMAL(15, 2))  # Coût unitaire au moment du mouvement
    statut = Column(String, default="validé")  # "validé", "annulé"