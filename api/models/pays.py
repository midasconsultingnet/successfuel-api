from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class Pays(BaseModel):
    __tablename__ = "pays"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(100), nullable=False)
    code = Column(String(3), unique=True)
