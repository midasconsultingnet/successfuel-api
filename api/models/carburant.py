from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
import uuid


class Carburant(Base):
    __tablename__ = "carburant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    libelle = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True)

    # Relationships
    cuves = relationship("Cuve", back_populates="carburant")