from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime, timezone
import uuid
from ..base import Base

class BaseModel(Base):
    """
    Modèle de base pour tous les modèles de l'application.
    Fournit des champs standardisés pour la gestion des dates, la gestion des transactions et le soft delete.
    """

    # L'héritage de Base garantit que tous les modèles dérivés sont enregistrés dans le même MetaData
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_creation = Column('created_at', DateTime(timezone=True), default=func.now(), nullable=False)
    date_modification = Column('updated_at', DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    est_actif = Column('est_actif', Boolean, default=True, nullable=False)

    def update_timestamp(self):
        """Met à jour la date de modification"""
        self.date_modification = datetime.now(timezone.utc)

    def soft_delete(self):
        """Méthode pour le soft delete"""
        self.est_actif = False
        self.update_timestamp()

    # Propriétés pour permettre l'accès aux champs via les noms Pydantic
    @property
    def created_at(self):
        return self.date_creation

    @created_at.setter
    def created_at(self, value):
        self.date_creation = value

    @property
    def updated_at(self):
        return self.date_modification

    @updated_at.setter
    def updated_at(self, value):
        self.date_modification = value

    __abstract__ = True  # Rend la classe abstraite pour éviter la création de table