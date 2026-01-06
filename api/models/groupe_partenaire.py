from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel


class GroupePartenaire(BaseModel):
    __tablename__ = "groupes_partenaire"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    infos_plus = Column(JSONB)  # Additional information in JSON format

    # Relationships
    stations = relationship("Station", back_populates="groupe_partenaire", lazy="select")