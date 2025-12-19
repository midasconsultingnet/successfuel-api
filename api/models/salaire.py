from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base_model import BaseModel

class Salaire(BaseModel):
    __tablename__ = "salaires"

    employe_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)  # Employee is a type of tier
    periode = Column(String, nullable=False)  # Format: YYYY-MM
    date_echeance = Column(DateTime(timezone=True), nullable=False)
    date_paiement = Column(DateTime(timezone=True))  # When was it paid
    salaire_base = Column(Float, nullable=False)
    montant_total = Column(Float, nullable=False)
    statut = Column(String, default="prevu")  # prevu, echu, paye, du
    methode_paiement = Column(String)  # cash, virement, cheque
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who processed the payment
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company
    station_id = Column(String, nullable=False)  # UUID of the station

class Prime(BaseModel):
    __tablename__ = "primes"

    employe_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    motif = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    periode = Column(String)  # Optional: to which period does this bonus apply
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who created the bonus
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company

class Avance(BaseModel):
    __tablename__ = "avances"

    employe_id = Column(PG_UUID(as_uuid=True), ForeignKey("tiers.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    motif = Column(String)
    date_echeance = Column(DateTime(timezone=True))  # When should it be repaid
    montant_rembourse = Column(Float, default=0)  # Amount repaid so far
    statut = Column(String, default="non_rembourse")  # non_rembourse, en_cours, rembourse
    utilisateur_id = Column(PG_UUID(as_uuid=True), ForeignKey("utilisateur.id"))  # ID of the user who created the advance
    numero_piece_comptable = Column(String)
    compagnie_id = Column(String, nullable=False)  # UUID of the company


class ElementPaie(BaseModel):
    __tablename__ = "elements_paie"

    code = Column(String, unique=True, nullable=False)  # Unique code for the pay element
    libelle = Column(String, nullable=False)  # Descriptive name of the pay element
    type_element = Column(String, nullable=False)  # "fixe", "variable", "cotisation", "avantage"
    categorie = Column(String, nullable=False)  # "salaire_de_base", "prime", "indemnite", "cotisation_salariale", "cotisation_patronale", etc.
    est_deductible = Column(Boolean, default=False)  # Whether it's deductible from gross pay
    est_imposable = Column(Boolean, default=True)  # Whether it's subject to taxation
    valeur_par_defaut = Column(Float, default=0)  # Default value for the pay element
    borne_inferieure = Column(Float)  # Lower limit for calculation
    borne_superieure = Column(Float)  # Upper limit for calculation
    pourcentage = Column(Float)  # Percentage value for calculation if applicable
    methode_calcul = Column(String)  # "fixe", "pourcentage", "quantite_temps", "progressif"
    est_actif = Column(Boolean, default=True)  # Whether the pay element is currently active
    ordre_affichage = Column(Integer, default=0)  # Display order in payslip
    compagnie_id = Column(String, nullable=False)  # UUID of the company
