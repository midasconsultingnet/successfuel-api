from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum as PyEnum
from .base_model import BaseModel


class ClassificationEcart(PyEnum):
    PERTE = "perte"
    EVAPORATION = "evaporation"
    ANOMALIE = "anomalie"
    SURPLUS = "surplus"


class EcartInventaire(BaseModel):
    __tablename__ = "ecart_inventaire"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventaire_id = Column(UUID(as_uuid=True), ForeignKey('inventaires.id'), nullable=False)
    produit_id = Column(UUID(as_uuid=True), ForeignKey('produit.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('station.id'), nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey('compagnie.id'), nullable=False)
    
    quantite_theorique = Column(Numeric(10, 2), nullable=False)  # Quantité attendue selon le système
    quantite_reelle = Column(Numeric(10, 2), nullable=False)     # Quantité trouvée lors de l'inventaire
    ecart = Column(Numeric(10, 2), nullable=False)               # Différence entre réel et théorique
    
    classification = Column(Enum(ClassificationEcart), nullable=False)  # Classification de l'écart
    seuil_alerte = Column(Numeric(10, 2))                      # Seuil qui a déclenché l'alerte
    seuil_saison = Column(Text)                                 # Informations sur le seuil saisonnier
    motif_anomalie = Column(Text)                               # Explication pour les anomalies
    
    # Relations
    inventaire = relationship("Inventaire", back_populates="ecarts")
    produit = relationship("Produit")
    station = relationship("Station")
    compagnie = relationship("Compagnie")


# Relation inverse dans la classe Inventaire
def link_inventaire_ecarts():
    """
    Fonction pour lier la relation entre Inventaire et EcartInventaire.
    Cette fonction est appelée pour éviter les problèmes d'import circulaire.
    """
    from .inventaire import Inventaire
    if not hasattr(Inventaire, 'ecarts'):
        Inventaire.ecarts = relationship("EcartInventaire", back_populates="inventaire")


# Appel de la fonction pour établir la liaison
link_inventaire_ecarts()