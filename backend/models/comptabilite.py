from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base
from datetime import datetime
import uuid

class JournalEntree(Base):
    __tablename__ = "journal_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_ecriture = Column(Date, nullable=False)
    libelle = Column(Text, nullable=False)
    type_operation = Column(String(30))  # Check constraint: 'Achat','Vente','Tresorerie','Stock','Autre','Ouverture','Regul'
    reference_operation = Column(String(100))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle l'écriture appartient
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    statut = Column(String(20), default='Actif')  # Check constraint: 'Actif', 'Inactif', 'Supprime'
    created_by = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    est_valide = Column(Boolean, default=False)
    valide_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    date_validation = Column(DateTime(timezone=True))
    type_document_origine = Column(String(50))
    document_origine_id = Column(UUID(as_uuid=True))
    est_ouverture = Column(Boolean, default=False)
    bilan_initial_id = Column(UUID(as_uuid=True), ForeignKey("bilan_initial.id"))
    
    __table_args__ = (
        CheckConstraint(
            type_operation.in_(['Achat', 'Vente', 'Tresorerie', 'Stock', 'Autre', 'Ouverture', 'Regul']),
            name='check_type_operation'
        ),
        CheckConstraint(
            statut.in_(['Actif', 'Inactif', 'Supprime']),
            name='check_statut_journal'
        )
    )

class JournalLigne(Base):
    __tablename__ = "journal_lines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    compte_num = Column(String(20))
    compte_id = Column(UUID(as_uuid=True), ForeignKey("plan_comptable.id"))
    debit = Column(Numeric(18,2), default=0)  # Check constraint: debit >= 0
    credit = Column(Numeric(18,2), default=0)  # Check constraint: credit >= 0
    sens = Column(String(1))  # Generated column: 'D' or 'C'
    
    __table_args__ = (
        CheckConstraint(debit >= 0, name='check_debit_positive'),
        CheckConstraint(credit >= 0, name='check_credit_positive'),
        CheckConstraint(sens.in_(['D', 'C']), name='check_sens_value')
    )

class EtatStock(Base):
    __tablename__ = "etat_stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_etat = Column(Date, nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    stock_initial = Column(Numeric(18,3), default=0)
    entrees = Column(Numeric(18,3), default=0)
    sorties = Column(Numeric(18,3), default=0)
    stock_final = Column(Numeric(18,3), default=0)
    valeur_stock = Column(Numeric(18,2), default=0)
    observation = Column(Text)
    statut = Column(String(20), default='Actif')
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class EtatCaisse(Base):
    __tablename__ = "etat_caisse"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_etat = Column(Date, nullable=False)
    tresorerie_id = Column(UUID(as_uuid=True), ForeignKey("tresoreries.id"), nullable=False)
    solde_initial = Column(Numeric(18,2), default=0)
    encaissements = Column(Numeric(18,2), default=0)
    decaissements = Column(Numeric(18,2), default=0)
    solde_final = Column(Numeric(18,2), default=0)
    ecart = Column(Numeric(18,2), default=0)
    observation = Column(Text)
    statut = Column(String(20), default='Actif')
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class EtatComptable(Base):
    __tablename__ = "etat_comptable"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_etat = Column(Date, nullable=False)
    compte_id = Column(UUID(as_uuid=True), ForeignKey("plan_comptable.id"), nullable=False)
    solde_initial = Column(Numeric(18,2), default=0)
    debit_periode = Column(Numeric(18,2), default=0)
    credit_periode = Column(Numeric(18,2), default=0)
    solde_final = Column(Numeric(18,2), default=0)
    observation = Column(Text)
    statut = Column(String(20), default='Actif')
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)