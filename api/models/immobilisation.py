from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel

class Immobilisation(BaseModel):
    __tablename__ = "immobilisations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    description = Column(String)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "matériel", "véhicule", "bâtiment", etc.
    date_acquisition = Column(DateTime, nullable=False)
    valeur_origine = Column(DECIMAL(15, 2), nullable=False)
    valeur_nette = Column(DECIMAL(15, 2))
    taux_amortissement = Column(DECIMAL(5, 2))
    duree_vie = Column(Integer)  # En années
    statut = Column(String, default="actif")  # "actif", "inactif", "cessionné", "hors_service"
    station_id = Column(UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)

class MouvementImmobilisation(BaseModel):
    __tablename__ = "mouvement_immobilisations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    immobilisation_id = Column(UUID(as_uuid=True), ForeignKey("immobilisations.id"), nullable=False)
    type_mouvement = Column(String, nullable=False)  # "acquisition", "amélioration", "cession", "sortie", "amortissement"
    date_mouvement = Column(DateTime, nullable=False)
    description = Column(String)
    valeur_variation = Column(DECIMAL(15, 2))
    valeur_apres_mouvement = Column(DECIMAL(15, 2))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    reference_document = Column(String)
    statut = Column(String, default="validé")  # "validé", "annulé"
