from sqlalchemy import Column, String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum as PyEnum
from ..base import Base
from .base_model import BaseModel


class TypeEcart(PyEnum):
    PRIX = "prix"
    QUANTITE = "quantite"
    PRODUIT = "produit"


class EcartPrix(BaseModel):
    __tablename__ = "ecart_prix"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_ecart = Column(Enum(TypeEcart), nullable=False)
    description = Column(Text, nullable=True)
    
    # Référence à la commande d'achat
    achat_id = Column(UUID(as_uuid=True), ForeignKey('achats.id'), nullable=False)
    achat = relationship("Achat", back_populates="ecarts_prix")
    
    # Référence au détail de la commande
    achat_detail_id = Column(UUID(as_uuid=True), ForeignKey('achats_details.id'), nullable=False)
    achat_detail = relationship("AchatDetail", back_populates="ecarts_prix")
    
    # Détails de l'écart
    valeur_demandee = Column(Numeric(10, 2), nullable=False)
    valeur_recue = Column(Numeric(10, 2), nullable=False)
    ecart_absolu = Column(Numeric(10, 2), nullable=False)
    taux_ecart = Column(Numeric(5, 2), nullable=False)  # Pourcentage d'écart
    
    # Statut de gestion de l'écart
    est_gere = Column(Boolean, default=False)
    date_gestion = Column(DateTime, nullable=True)
    utilisateur_gestion_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=True)
    utilisateur_gestion = relationship("User", back_populates="ecarts_prix_geres")


# Ajout des relations inverses aux modèles existants
def add_relationships_to_existing_models():
    """
    Cette fonction est appelée pour ajouter les relations aux modèles existants
    sans avoir à réécrire l'ensemble des modèles
    """
    from sqlalchemy.orm import relationship
    from .achat import Achat, AchatDetail
    from .user import User
    
    # Ajout de la relation à Achat
    Achat.ecarts_prix = relationship("EcartPrix", back_populates="achat")
    
    # Ajout de la relation à AchatDetail
    AchatDetail.ecarts_prix = relationship("EcartPrix", back_populates="achat_detail")
    
    # Ajout de la relation à User
    User.ecarts_prix_geres = relationship("EcartPrix", back_populates="utilisateur_gestion")


# Appeler la fonction pour établir les relations
add_relationships_to_existing_models()