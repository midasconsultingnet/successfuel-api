from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..models.base_model import BaseModel


class AuditExport(BaseModel):
    __tablename__ = "audit_exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    type_bilan = Column(String, nullable=False)  # tresorerie, tiers, operations, etc.
    format_export = Column(String, nullable=False)  # csv, json
    date_export = Column(DateTime, nullable=False)
    fichier_genere = Column(String)  # Chemin ou nom du fichier exporté
    taille_fichier = Column(Integer)  # Taille du fichier en octets
    ip_utilisateur = Column(String)
    user_agent = Column(String)
    details = Column(Text)  # Détails additionnels sur l'export
    statut = Column(String, default="complet")  # complet, partiel, erreur