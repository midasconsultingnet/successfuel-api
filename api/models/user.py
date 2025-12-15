from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class User(BaseModel):
    __tablename__ = "utilisateur"  # Changed to match the actual database table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    login = Column(String(255), unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # gerant_compagnie, utilisateur_compagnie
    date_derniere_connexion = Column(DateTime)
    actif = Column(Boolean, default=True)
    compagnie_id = Column(UUID(as_uuid=True))  # Changed to proper UUID type

