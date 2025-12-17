from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Boolean, ForeignKey, DECIMAL, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from .base_model import BaseModel
from datetime import datetime
import uuid

class Tresorerie(BaseModel):
    __tablename__ = "tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    type = Column(String, nullable=False)  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde_initial = Column(DECIMAL(15, 2), nullable=False)
    devise = Column(String, default='XOF')
    informations_bancaires = Column(JSONB)  # JSONB for bank details
    statut = Column(String, default='actif')  # actif, inactif
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)

class TresorerieStation(BaseModel):
    __tablename__ = "tresorerie_station"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trésorerie_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie.id"), nullable=False)
    station_id = Column(PG_UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    solde_initial = Column(DECIMAL(15, 2), nullable=False)
    solde_actuel = Column(DECIMAL(15, 2), default=0)

    # Relationships
    tresorerie = relationship("Tresorerie", lazy="select")
    station = relationship("Station", lazy="select")
    mouvements = relationship("MouvementTresorerie", back_populates="trésorerie_station", lazy="select")
    ventes = relationship("Vente", back_populates="trésorerie_station", lazy="select")

    __table_args__ = (
        Index('idx_tresorerie_station_station_id', 'station_id'),
        Index('idx_tresorerie_station_trésorerie_id', 'trésorerie_id'),
    )


class EtatInitialTresorerie(BaseModel):
    __tablename__ = "etat_initial_tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tresorerie_station_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    date_enregistrement = Column(Date, nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    commentaire = Column(String)
    enregistre_par = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)

class MouvementTresorerie(BaseModel):
    __tablename__ = "mouvement_tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trésorerie_station_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    type_mouvement = Column(String, nullable=False)  # entrée, sortie
    montant = Column(DECIMAL(15, 2), nullable=False)
    date_mouvement = Column(DateTime, nullable=False)
    description = Column(String)
    module_origine = Column(String, nullable=False)
    reference_origine = Column(String, nullable=False)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    numero_piece_comptable = Column(String)
    statut = Column(String, default='validé')  # validé, annulé
    methode_paiement_id = Column(PG_UUID(as_uuid=True), ForeignKey("methode_paiement.id"))  # Ajout de la méthode de paiement

    # Relationships
    trésorerie_station = relationship("TresorerieStation", back_populates="mouvements", lazy="select")
    utilisateur = relationship("User", lazy="select")
    methode_paiement = relationship("MethodePaiement", lazy="select")

    __table_args__ = (
        Index('idx_mouvement_tresorerie_station_id', 'trésorerie_station_id'),
        Index('idx_mouvement_tresorerie_type_mouvement', 'type_mouvement'),
        Index('idx_mouvement_tresorerie_date', 'date_mouvement'),
        Index('idx_mouvement_tresorerie_statut', 'statut'),
        Index('idx_mouvement_tresorerie_utilisateur_id', 'utilisateur_id'),
        Index('idx_mouvement_tresorerie_module_origine', 'module_origine'),
    )

class TransfertTresorerie(BaseModel):
    __tablename__ = "transfert_tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trésorerie_source_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    trésorerie_destination_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    date_transfert = Column(DateTime, nullable=False)
    description = Column(String)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    statut = Column(String, default='validé')  # validé, annulé
