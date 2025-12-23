from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Boolean, ForeignKey, DECIMAL, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from .base_model import BaseModel
from datetime import datetime, timezone
import uuid

class Tresorerie(BaseModel):
    __tablename__ = "tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String, nullable=False)
    type = Column(String, nullable=False)  # caisse, banque, mobile_money, note_credit, coffre, fonds_divers
    solde_initial = Column(DECIMAL(15, 2), nullable=True)
    solde_tresorerie = Column(DECIMAL(15, 2), default=0)  # Solde global calculé à partir des mouvements
    devise = Column(String, default='XOF')
    informations_bancaires = Column(JSONB)  # JSONB for bank details
    statut = Column(String, default='actif')  # actif, inactif
    compagnie_id = Column(PG_UUID(as_uuid=True), ForeignKey("compagnie.id"), nullable=False)

class TresorerieStation(BaseModel):
    __tablename__ = "tresorerie_station"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tresorerie_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie.id"), nullable=False)
    station_id = Column(PG_UUID(as_uuid=True), ForeignKey("station.id"), nullable=False)
    # Le champ solde_initial a été supprimé car il est redondant avec les vues matérialisées
    # Le solde_initial est maintenant géré via la table etat_initial_tresorerie
    # Le champ solde_actuel a été supprimé car il est redondant avec les vues matérialisées
    # Le solde actuel est maintenant calculé via la vue matérialisée vue_solde_tresorerie_station

    # Relationships
    tresorerie = relationship("Tresorerie", lazy="select")
    station = relationship("Station", lazy="select")
    mouvements = relationship("MouvementTresorerie", back_populates="trésorerie_station", lazy="select")
    ventes = relationship("Vente", back_populates="trésorerie_station", lazy="select")
    paiements_achat_carburant = relationship("PaiementAchatCarburant", back_populates="tresorerie_station", lazy="select")

    __table_args__ = (
        Index('idx_tresorerie_station_station_id', 'station_id'),
        Index('idx_tresorerie_station_tresorerie_id', 'tresorerie_id'),
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
    tresorerie_station_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    type_mouvement = Column(String, nullable=False)  # entrée, sortie
    montant = Column(DECIMAL(15, 2), nullable=False)
    date_mouvement = Column(DateTime(timezone=True), nullable=False)
    description = Column(String)
    module_origine = Column(String, nullable=False)
    reference_origine = Column(String, nullable=False)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    numero_piece_comptable = Column(String)
    statut = Column(String, default='validé')  # validé, annulé
    est_annule = Column(Boolean, default=False)  # Nouveau champ pour la gestion des annulations
    mouvement_origine_id = Column(PG_UUID(as_uuid=True), ForeignKey("mouvement_tresorerie.id"))  # Référence vers le mouvement original en cas d'annulation
    methode_paiement_id = Column(PG_UUID(as_uuid=True), ForeignKey("methode_paiement.id"))  # Ajout de la méthode de paiement

    # Relationships
    trésorerie_station = relationship("TresorerieStation", back_populates="mouvements", lazy="select")
    utilisateur = relationship("User", lazy="select")
    methode_paiement = relationship("MethodePaiement", lazy="select")
    mouvement_origine = relationship("MouvementTresorerie", remote_side=[id], backref="mouvements_inverses")  # Relation pour les mouvements d'annulation

    __table_args__ = (
        Index('idx_mouvement_tresorerie_station_id', 'tresorerie_station_id'),
        Index('idx_mouvement_tresorerie_type_mouvement', 'type_mouvement'),
        Index('idx_mouvement_tresorerie_date', 'date_mouvement'),
        Index('idx_mouvement_tresorerie_statut', 'statut'),
        Index('idx_mouvement_tresorerie_utilisateur_id', 'utilisateur_id'),
        Index('idx_mouvement_tresorerie_module_origine', 'module_origine'),
        Index('idx_mouvement_tresorerie_est_annule', 'est_annule'),  # Index pour les mouvements annulés
    )

class TransfertTresorerie(BaseModel):
    __tablename__ = "transfert_tresorerie"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trésorerie_source_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    trésorerie_destination_id = Column(PG_UUID(as_uuid=True), ForeignKey("tresorerie_station.id"), nullable=False)
    montant = Column(DECIMAL(15, 2), nullable=False)
    date_transfert = Column(DateTime(timezone=True), nullable=False)
    description = Column(String)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    statut = Column(String, default='validé')  # validé, annulé
