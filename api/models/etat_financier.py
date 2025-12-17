from sqlalchemy import Column, String, DateTime, Date, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel


class EtatFinancier(BaseModel):
    __tablename__ = "etat_financier"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_etat = Column(String, nullable=False)  # "tresorerie", "tiers", "stocks", "bilan_operations", "journal_operations", "journal_comptable", "bilan_initial", "etat_resultat"
    nom_etat = Column(String(255), nullable=False)  # Nom de l'état financier
    periode_debut = Column(Date, nullable=False)  # Début de la période de l'état financier
    periode_fin = Column(Date, nullable=False)  # Fin de la période de l'état financier
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"))  # Référence à une station (optionnel - NULL pour consolidé)
    utilisateur_generation_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID de l'utilisateur qui a généré l'état
    date_generation = Column(DateTime, nullable=False)  # Date de génération de l'état
    parametres_filtrage = Column(JSON)  # Paramètres de filtrage pour la génération de l'état
    statut = Column(String, default="en_cours")  # "en_cours", "genere", "valide"
    fichier_export = Column(String(500))  # Chemin vers le fichier exporté (optionnel)