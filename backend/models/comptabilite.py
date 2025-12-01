from sqlalchemy import Column, String, Text, Integer, Float, Numeric, Date, DateTime, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import expression
import uuid
from datetime import datetime

Base = declarative_base()

class PlanComptable(Base):
    __tablename__ = 'plan_comptable'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(20), unique=True, nullable=False)
    intitule = Column(String(255), nullable=False)
    classe = Column(String(5), nullable=False)
    type_compte = Column(String(100), nullable=False)
    sens_solde = Column(String(10))
    description = Column(Text)
    statut = Column(String(20), default='Actif', nullable=False)
    est_compte_racine = Column(Boolean, default=False)
    est_compte_de_resultat = Column(Boolean, default=False)
    est_compte_actif = Column(Boolean, default=True)
    pays_id = Column(PostgresUUID(as_uuid=True), ForeignKey('pays.id'))
    est_specifique_pays = Column(Boolean, default=False)
    code_pays = Column(String(3))
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relation avec le compte parent (auto-référentielle)
    compte_parent_id = Column(PostgresUUID(as_uuid=True), ForeignKey('plan_comptable.id'))
    compte_parent = relationship("PlanComptable", remote_side=[id])

    # Relations vers les écritures
    ecritures = relationship("EcritureComptable", secondary="lignes_ecritures", back_populates="comptes", overlaps="lignes,comptes,journal")
    lignes_ecritures = relationship("LigneEcriture", back_populates="compte", overlaps="ecritures")

    __table_args__ = (
        Index('idx_plan_comptable_numero', 'numero'),
        Index('idx_plan_comptable_classe', 'classe'),
        Index('idx_plan_comptable_type', 'type_compte'),
        Index('idx_plan_comptable_parent', 'compte_parent_id'),
        Index('idx_plan_comptable_pays', 'pays_id'),
        Index('idx_plan_comptable_compagnie', 'compagnie_id'),
        Index('idx_plan_comptable_statut', 'statut'),
        CheckConstraint("statut IN ('Actif', 'Inactif', 'Supprime')", name="plan_comptable_statut_check"),
        CheckConstraint("sens_solde IN ('D', 'C')", name="plan_comptable_sens_solde_check"),
    )

class Journal(Base):
    __tablename__ = 'journaux'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    libelle = Column(String(100), nullable=False)
    observation = Column(Text)
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'))
    type_journal = Column(String(50), nullable=False)
    statut = Column(String(20), default='Actif', nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relation avec les écritures
    ecritures = relationship("EcritureComptable", back_populates="journal")

    __table_args__ = (
        Index('idx_journaux_code', 'code'),
        Index('idx_journaux_type', 'type_journal'),
        Index('idx_journaux_compagnie', 'compagnie_id'),
        Index('idx_journaux_statut', 'statut'),
        CheckConstraint("type_journal IN ('achats', 'ventes', 'tresorerie', 'banque', 'caisse', 'opex', 'stock', 'autre')", name="journal_type_check"),
        CheckConstraint("statut IN ('Actif', 'Inactif', 'Supprime')", name="journal_statut_check"),
    )

class EcritureComptable(Base):
    __tablename__ = 'ecritures_comptables'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_id = Column(PostgresUUID(as_uuid=True), ForeignKey('journaux.id'), nullable=False)
    numero_piece = Column(String(50), nullable=False)
    date_ecriture = Column(Date, nullable=False)
    libelle = Column(Text, nullable=False)
    montant_debit = Column(Numeric(18, 2), default=0)
    montant_credit = Column(Numeric(18, 2), default=0)
    tiers_id = Column(PostgresUUID(as_uuid=True))
    utilisateur_id = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    operation_id = Column(PostgresUUID(as_uuid=True))
    operation_type = Column(String(50))
    est_validee = Column(Boolean, default=False)
    est_cloturee = Column(Boolean, default=False)
    date_validation = Column(DateTime(timezone=True))
    utilisateur_validation_id = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    reference_externe = Column(String(100))
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relations
    journal = relationship("Journal", back_populates="ecritures", overlaps="comptes,lignes")
    lignes = relationship("LigneEcriture", back_populates="ecriture", cascade="all, delete-orphan", overlaps="ecritures,comptes,journal")
    comptes = relationship("PlanComptable", secondary="lignes_ecritures", back_populates="ecritures", overlaps="lignes,journal,compte,lignes_ecritures")

    # Contrainte d'unicité
    __table_args__ = (
        UniqueConstraint('journal_id', 'numero_piece', name='unique_journal_piece'),
        Index('idx_ecritures_journal_piece', 'journal_id', 'numero_piece'),
        Index('idx_ecritures_date', 'date_ecriture'),
        Index('idx_ecritures_tiers', 'tiers_id'),
        Index('idx_ecritures_utilisateur', 'utilisateur_id'),
        Index('idx_ecritures_operation', 'operation_id', 'operation_type'),
        Index('idx_ecritures_validee', 'est_validee'),
        Index('idx_ecritures_cloturee', 'est_cloturee'),
        Index('idx_ecritures_compagnie', 'compagnie_id'),
    )

    @hybrid_property
    def est_equilibree(self):
        return abs(float(self.montant_debit) - float(self.montant_credit)) < 0.01

    def check_balance(self):
        """Vérifie si l'écriture est équilibrée en débit et crédit"""
        total_debit = sum(ligne.montant_debit for ligne in self.lignes)
        total_credit = sum(ligne.montant_credit for ligne in self.lignes)
        return abs(float(total_debit) - float(total_credit)) < 0.01


class LigneEcriture(Base):
    __tablename__ = 'lignes_ecritures'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ecriture_id = Column(PostgresUUID(as_uuid=True), ForeignKey('ecritures_comptables.id'), nullable=False)
    compte_id = Column(PostgresUUID(as_uuid=True), ForeignKey('plan_comptable.id'), nullable=False)
    montant_debit = Column(Numeric(18, 2), default=0)
    montant_credit = Column(Numeric(18, 2), default=0)
    libelle = Column(Text)
    tiers_id = Column(PostgresUUID(as_uuid=True))
    projet_id = Column(PostgresUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    # Relations
    ecriture = relationship("EcritureComptable", back_populates="lignes", overlaps="comptes,ecritures")
    compte = relationship("PlanComptable", overlaps="lignes,ecritures,comptes")

    __table_args__ = (
        Index('idx_lignes_ecriture', 'ecriture_id'),
        Index('idx_lignes_compte', 'compte_id'),
        Index('idx_lignes_tiers', 'tiers_id'),
        Index('idx_lignes_projet', 'projet_id'),
        # Check constraint to ensure debit or credit but not both
        CheckConstraint(
            "(montant_debit > 0 AND montant_credit = 0) OR "
            "(montant_credit > 0 AND montant_debit = 0) OR "
            "(montant_debit = 0 AND montant_credit = 0)",
            name="check_montant_uniquement_debit_ou_credit"
        ),
    )

class SoldeCompte(Base):
    __tablename__ = 'soldes_comptes'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compte_id = Column(PostgresUUID(as_uuid=True), ForeignKey('plan_comptable.id'), nullable=False)
    date_solde = Column(Date, nullable=False)
    solde_debit = Column(Numeric(18, 2), default=0)
    solde_credit = Column(Numeric(18, 2), default=0)
    type_solde = Column(String(20), nullable=False)
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    # Calculé automatiquement
    @hybrid_property
    def solde_net(self):
        return float(self.solde_debit) - float(self.solde_credit)

    __table_args__ = (
        UniqueConstraint('compte_id', 'date_solde', 'compagnie_id', name='unique_solde_compte_date_compagnie'),
        Index('idx_soldes_compte', 'compte_id'),
        Index('idx_soldes_date', 'date_solde'),
        Index('idx_soldes_compagnie', 'compagnie_id'),
        Index('idx_soldes_type', 'type_solde'),
        CheckConstraint("type_solde IN ('ouverture', 'cloture', 'intermediaire')", name="solde_compte_type_check"),
    )

class BilanInitial(Base):
    __tablename__ = 'bilan_initial'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'))
    date_bilan_initial = Column(Date, nullable=False)
    est_valide = Column(Boolean, default=False)
    est_verifie = Column(Boolean, default=False)
    commentaire = Column(Text)
    utilisateur_id = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relations
    lignes = relationship("BilanInitialLigne", back_populates="bilan_initial", cascade="all, delete-orphan")
    immobilisations = relationship("ImmobilisationBilanInitial", back_populates="bilan_initial", cascade="all, delete-orphan")
    stocks = relationship("StockBilanInitial", back_populates="bilan_initial", cascade="all, delete-orphan")
    creances_dettes = relationship("CreanceDetteBilanInitial", back_populates="bilan_initial", cascade="all, delete-orphan")
    journaux_entree = relationship("JournalEntree", back_populates="bilan_initial", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_bilan_initial_compagnie', 'compagnie_id'),
        Index('idx_bilan_initial_date', 'date_bilan_initial'),
        Index('idx_bilan_initial_utilisateur', 'utilisateur_id'),
        Index('idx_bilan_initial_validation', 'est_valide', 'est_verifie'),
    )

class BilanInitialLigne(Base):
    __tablename__ = 'bilan_initial_lignes'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bilan_initial_id = Column(PostgresUUID(as_uuid=True), ForeignKey('bilan_initial.id'), nullable=False)
    compte_numero = Column(String(20), nullable=False)
    compte_id = Column(PostgresUUID(as_uuid=True), ForeignKey('plan_comptable.id'))
    montant_initial = Column(Numeric(18, 2), nullable=False)
    type_solde = Column(String(10))
    poste_bilan = Column(String(20), nullable=False)
    categorie_detaillee = Column(String(50))
    commentaire = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    # Relations
    bilan_initial = relationship("BilanInitial", back_populates="lignes")
    compte = relationship("PlanComptable")

    __table_args__ = (
        Index('idx_bilan_initial_lignes_bilan', 'bilan_initial_id'),
        Index('idx_bilan_initial_lignes_compte', 'compte_numero'),
        Index('idx_bilan_initial_lignes_poste', 'poste_bilan'),
        Index('idx_bilan_initial_lignes_montant', 'montant_initial'),
        CheckConstraint("type_solde IN ('debit', 'credit')", name="bilan_initial_ligne_type_solde_check"),
        CheckConstraint("poste_bilan IN ('actif', 'passif', 'capitaux_propres')", name="bilan_initial_ligne_poste_bilan_check"),
    )

class ImmobilisationBilanInitial(Base):
    __tablename__ = 'immobilisations_bilan_initial'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bilan_initial_id = Column(PostgresUUID(as_uuid=True), ForeignKey('bilan_initial.id'), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    libelle = Column(Text, nullable=False)
    categorie = Column(String(100), nullable=False)
    date_achat = Column(Date, nullable=False)
    valeur_acquisition = Column(Numeric(18, 2), nullable=False)
    valeur_nette_comptable = Column(Numeric(18, 2), nullable=False)
    amortissement_cumule = Column(Numeric(18, 2), nullable=False)
    duree_amortissement = Column(Integer, default=0)
    date_fin_amortissement = Column(Date)
    fournisseur_id = Column(PostgresUUID(as_uuid=True), ForeignKey('fournisseurs.id'))
    utilisateur_achat_id = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    observation = Column(Text)
    statut = Column(String(20), default='Actif', nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relations
    bilan_initial = relationship("BilanInitial", back_populates="immobilisations")

    __table_args__ = (
        Index('idx_immob_bilan_initial_bilan', 'bilan_initial_id'),
        Index('idx_immob_bilan_initial_code', 'code'),
        CheckConstraint("statut IN ('Actif', 'Cede', 'Hors service', 'Vendu')", name="immobilisation_statut_check"),
    )

class StockBilanInitial(Base):
    __tablename__ = 'stocks_bilan_initial'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bilan_initial_id = Column(PostgresUUID(as_uuid=True), ForeignKey('bilan_initial.id'), nullable=False)
    type_stock = Column(String(20), nullable=False)
    article_id = Column(PostgresUUID(as_uuid=True), ForeignKey('articles.id'))
    carburant_id = Column(PostgresUUID(as_uuid=True), ForeignKey('carburants.id'))
    cuve_id = Column(PostgresUUID(as_uuid=True), ForeignKey('cuves.id'))
    quantite = Column(Numeric(18, 3), nullable=False)
    prix_unitaire = Column(Numeric(18, 4), nullable=False)
    commentaire = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    # Calculé automatiquement
    @hybrid_property
    def valeur_totale(self):
        return float(self.quantite) * float(self.prix_unitaire)

    # Relations
    bilan_initial = relationship("BilanInitial", back_populates="stocks")

    __table_args__ = (
        Index('idx_stocks_bilan_initial_bilan', 'bilan_initial_id'),
        Index('idx_stocks_bilan_initial_article', 'article_id'),
        Index('idx_stocks_bilan_initial_carburant', 'carburant_id'),
        Index('idx_stocks_bilan_initial_type', 'type_stock'),
        CheckConstraint("type_stock IN ('carburant', 'produit_boutique')", name="stock_bilan_initial_type_check"),
    )

class CreanceDetteBilanInitial(Base):
    __tablename__ = 'creances_dettes_bilan_initial'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bilan_initial_id = Column(PostgresUUID(as_uuid=True), ForeignKey('bilan_initial.id'), nullable=False)
    type_tiers = Column(String(20), nullable=False)
    tiers_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    montant_initial = Column(Numeric(18, 2), nullable=False)
    devise = Column(String(3), default='MGA')
    date_echeance = Column(Date)
    reference_piece = Column(String(100))
    commentaire = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    # Relations
    bilan_initial = relationship("BilanInitial", back_populates="creances_dettes")

    __table_args__ = (
        Index('idx_creances_dettes_bilan_initial_bilan', 'bilan_initial_id'),
        Index('idx_creances_dettes_bilan_initial_tiers', 'tiers_id'),
        Index('idx_creances_dettes_bilan_initial_type', 'type_tiers'),
        Index('idx_creances_dettes_bilan_initial_montant', 'montant_initial'),
        CheckConstraint("type_tiers IN ('client', 'fournisseur')", name="creance_dette_type_tiers_check"),
    )

class RapportFinancier(Base):
    __tablename__ = 'rapports_financiers'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_rapport = Column(String(50), nullable=False)  # 'bilan', 'compte_resultat', 'grand_livre', 'balance', 'journal', 'tva', 'etat_tva'
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    contenu = Column(JSONB)
    format_sortie = Column(String(20), default='PDF')
    statut = Column(String(20), default='En cours')
    utilisateur_generateur_id = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'))
    station_id = Column(PostgresUUID(as_uuid=True), ForeignKey('stations.id'))
    fichier_joint = Column(Text)  # Lien ou nom du fichier de rapport généré
    commentaire = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)


    __table_args__ = (
        Index('idx_rapports_financiers_type', 'type_rapport'),
        Index('idx_rapports_financiers_periode', 'periode_debut', 'periode_fin'),
        Index('idx_rapports_financiers_utilisateur', 'utilisateur_generateur_id'),
        Index('idx_rapports_financiers_compagnie', 'compagnie_id'),
        Index('idx_rapports_financiers_station', 'station_id'),
        Index('idx_rapports_financiers_date', 'created_at'),
        Index('idx_rapports_financiers_statut', 'statut'),
        CheckConstraint("statut IN ('En cours', 'Termine', 'Erreur', 'Archive')", name="rapport_financier_statut_check"),
    )

class HistoriqueRapport(Base):
    __tablename__ = 'historique_rapports'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_rapport = Column(String(100), nullable=False)  # Nom du rapport (ex: "Bilan mensuel")
    type_rapport = Column(String(50), nullable=False)  # Type de rapport
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    utilisateur_demandeur_id = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    utilisateur_generation_id = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    statut = Column(String(20), default='Demande')
    parametres = Column(JSONB)  # Paramètres utilisés pour la génération
    resultat_generation = Column(Text)  # Résultat de la génération (succès/erreur)
    date_demande = Column(DateTime(timezone=True), default=datetime.now)
    date_generation = Column(DateTime(timezone=True))
    date_consultation = Column(DateTime(timezone=True))
    est_a_jour = Column(Boolean, default=False)
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'))
    station_id = Column(PostgresUUID(as_uuid=True), ForeignKey('stations.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)


    __table_args__ = (
        Index('idx_historique_rapports_type', 'type_rapport'),
        Index('idx_historique_rapports_periode', 'periode_debut', 'periode_fin'),
        Index('idx_historique_rapports_demandeur', 'utilisateur_demandeur_id'),
        Index('idx_historique_rapports_generation', 'utilisateur_generation_id'),
        Index('idx_historique_rapports_date', 'created_at'),
        Index('idx_historique_rapports_a_jour', 'est_a_jour'),
        CheckConstraint("statut IN ('Demande', 'En cours', 'Termine', 'Erreur', 'Archive')", name="historique_rapport_statut_check"),
    )


class JournalEntree(Base):
    __tablename__ = 'journaux_entree'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_ecriture = Column(Date, nullable=False)
    libelle = Column(Text, nullable=False)
    type_operation = Column(String(50))
    reference_operation = Column(String(100))
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'), nullable=False)
    pays_id = Column(PostgresUUID(as_uuid=True), ForeignKey('pays.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)
    statut = Column(String(20), default='Actif', nullable=False)
    created_by = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    est_valide = Column(Boolean, default=False)
    valide_par = Column(PostgresUUID(as_uuid=True), ForeignKey('utilisateurs.id'))
    date_validation = Column(DateTime(timezone=True))
    type_document_origine = Column(String(50))
    document_origine_id = Column(PostgresUUID(as_uuid=True))
    est_ouverture = Column(Boolean, default=False)
    bilan_initial_id = Column(PostgresUUID(as_uuid=True), ForeignKey('bilan_initial.id'))

    # Relation
    bilan_initial = relationship("BilanInitial", back_populates="journaux_entree")

    __table_args__ = (
        Index('idx_journaux_entree_date', 'date_ecriture'),
        Index('idx_journaux_entree_compagnie', 'compagnie_id'),
        Index('idx_journaux_entree_pays', 'pays_id'),
        Index('idx_journaux_entree_validation', 'est_valide'),
        CheckConstraint("statut IN ('Actif', 'Inactif', 'Supprime')", name="journal_entree_statut_check"),
    )


class JournalLigne(Base):
    __tablename__ = 'journaux_lignes'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id = Column(PostgresUUID(as_uuid=True), ForeignKey('journaux_entree.id'), nullable=False)
    compte_num = Column(String(20))  # Numéro de compte au lieu de l'ID pour flexibilité
    compte_id = Column(PostgresUUID(as_uuid=True), ForeignKey('plan_comptable.id'))
    debit = Column(Numeric(18, 2), default=0)
    credit = Column(Numeric(18, 2), default=0)
    sens = Column(String(1))  # 'D' pour débit, 'C' pour crédit
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    # Relation
    journal_entree = relationship("JournalEntree", back_populates="lignes")

    __table_args__ = (
        Index('idx_journaux_lignes_entry', 'entry_id'),
        Index('idx_journaux_lignes_compte', 'compte_id'),
        Index('idx_journaux_lignes_sens', 'sens'),
        CheckConstraint("sens IN ('D', 'C')", name="journal_ligne_sens_check"),
    )


# Ajout de la relation dans JournalEntree après sa déclaration
JournalEntree.lignes = relationship("JournalLigne", back_populates="journal_entree", cascade="all, delete-orphan")


class EtatStock(Base):
    __tablename__ = 'etats_stock'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_etat = Column(Date, nullable=False)
    article_id = Column(PostgresUUID(as_uuid=True), ForeignKey('articles.id'), nullable=False)
    station_id = Column(PostgresUUID(as_uuid=True), ForeignKey('stations.id'), nullable=False)
    stock_initial = Column(Numeric(18, 3), default=0)
    entrees = Column(Numeric(18, 3), default=0)
    sorties = Column(Numeric(18, 3), default=0)
    stock_final = Column(Numeric(18, 3), default=0)
    valeur_stock = Column(Numeric(18, 2), default=0)
    observation = Column(Text)
    statut = Column(String(20), default='Actif', nullable=False)
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        Index('idx_etats_stock_date', 'date_etat'),
        Index('idx_etats_stock_article', 'article_id'),
        Index('idx_etats_stock_station', 'station_id'),
        Index('idx_etats_stock_compagnie', 'compagnie_id'),
        CheckConstraint("statut IN ('Actif', 'Inactif', 'Supprime')", name="etat_stock_statut_check"),
    )


class EtatCaisse(Base):
    __tablename__ = 'etats_caisse'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_etat = Column(Date, nullable=False)
    tresorerie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('tresoreries.id'), nullable=False)
    solde_initial = Column(Numeric(18, 2), default=0)
    encaissements = Column(Numeric(18, 2), default=0)
    decaissements = Column(Numeric(18, 2), default=0)
    solde_final = Column(Numeric(18, 2), default=0)
    ecart = Column(Numeric(18, 2), default=0)  # Différence entre le solde théorique et réel
    observation = Column(Text)
    statut = Column(String(20), default='Actif', nullable=False)
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        Index('idx_etats_caisse_date', 'date_etat'),
        Index('idx_etats_caisse_tresorerie', 'tresorerie_id'),
        Index('idx_etats_caisse_compagnie', 'compagnie_id'),
        CheckConstraint("statut IN ('Actif', 'Inactif', 'Supprime')", name="etat_caisse_statut_check"),
    )


class EtatComptable(Base):
    __tablename__ = 'etats_comptable'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_etat = Column(Date, nullable=False)
    compte_id = Column(PostgresUUID(as_uuid=True), ForeignKey('plan_comptable.id'), nullable=False)
    solde_initial = Column(Numeric(18, 2), default=0)
    debit_periode = Column(Numeric(18, 2), default=0)
    credit_periode = Column(Numeric(18, 2), default=0)
    solde_final = Column(Numeric(18, 2), default=0)
    observation = Column(Text)
    statut = Column(String(20), default='Actif', nullable=False)
    compagnie_id = Column(PostgresUUID(as_uuid=True), ForeignKey('compagnies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        Index('idx_etats_comptable_date', 'date_etat'),
        Index('idx_etats_comptable_compte', 'compte_id'),
        Index('idx_etats_comptable_compagnie', 'compagnie_id'),
        CheckConstraint("statut IN ('Actif', 'Inactif', 'Supprime')", name="etat_comptable_statut_check"),
    )