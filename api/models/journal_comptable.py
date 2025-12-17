from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel


class JournalComptable(BaseModel):
    __tablename__ = "journal_comptable"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)  # Nom du journal comptable
    code = Column(String(50), nullable=False, unique=True)  # Code unique du journal
    description = Column(String(500))  # Description du journal
    type_journal = Column(String(100), nullable=False)  # Ex: 'ventes', 'achats', 'tresorerie', 'banque', 'caisse', 'OD'
    devise = Column(String(10), default="XOF")  # Devise du journal
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)  # ID de l'utilisateur gestionnaire
    est_actif = Column(String(10), default="oui")  # Est-ce que le journal est actif