from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base_model import BaseModel


class Charge(BaseModel):
    __tablename__ = "charges"

    station_id = Column(String, nullable=False)  # UUID of the station
    categorie = Column(String, nullable=False)  # electricite, eau, fournitures, maintenance, etc.
    fournisseur_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"))  # Optional - service provider
    date = Column(DateTime(timezone=True), nullable=False)
    montant = Column(Float, nullable=False)
    description = Column(String)
    date_echeance = Column(DateTime(timezone=True))
    statut = Column(String, default="prevu")  # prevu, echu, paye, en_cours_paiement
    methode_paiement = Column(String)  # cash, cheque, virement, mobile_money
    numero_piece_comptable = Column(String)
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who recorded the expense
    solde_du = Column(Float, default=0)  # Remaining amount to be paid
    compagnie_id = Column(String, nullable=False)  # UUID of the company

    # Fields for recurring charges
    est_recurrente = Column(Boolean, default=False)
    frequence_recurrence = Column(String)  # quotidienne, hebdomadaire, mensuelle, etc.
    date_prochaine_occurrence = Column(Date)  # Next due date for recurring charges
    seuil_alerte = Column(Float)  # Threshold for budget alerts
    arret_compte = Column(Boolean, default=False)  # Flag to stop account for payment issues


class PaiementCharge(BaseModel):
    __tablename__ = "paiements_charges"

    charge_id = Column(PG_UUID(as_uuid=True), ForeignKey("charges.id"), nullable=False)
    date_paiement = Column(DateTime(timezone=True), nullable=False)
    montant_paye = Column(Float, nullable=False)
    methode_paiement = Column(String)  # cash, cheque, virement, mobile_money
    reference_paiement = Column(String)  # Transaction reference
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who processed the payment
    commentaire = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company


class CategorieCharge(BaseModel):
    __tablename__ = "categories_charges"

    nom = Column(String, unique=True, nullable=False)
    description = Column(String)
    type = Column(String)  # fixe, variable
    seuil_alerte = Column(Float)  # Threshold for budget alerts
    compte_comptable = Column(String)  # Accounting account
    compagnie_id = Column(String, nullable=False)  # UUID of the company