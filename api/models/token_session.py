from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class TokenSession(BaseModel):
    __tablename__ = "token_session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    token = Column(String, nullable=False)
    token_refresh = Column(String, nullable=False)
    date_expiration = Column(DateTime, nullable=False)
    actif = Column(Boolean, default=True)
