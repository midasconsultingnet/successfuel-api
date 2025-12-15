from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class JournalActionUtilisateur(BaseModel):
    __tablename__ = "journal_action_utilisateur"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    date_action = Column(DateTime, default=func.now(), nullable=False)
    type_action = Column(String, nullable=False)  # create, update, delete, read
    module_concerne = Column(String, nullable=False)
    donnees_avant = Column(Text)
    donnees_apres = Column(Text)
    ip_utilisateur = Column(String)
    user_agent = Column(String)
