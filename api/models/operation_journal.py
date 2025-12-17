from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base_model import BaseModel


class OperationJournal(BaseModel):
    __tablename__ = "operation_journal"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_operations_id = Column(UUID(as_uuid=True), ForeignKey("journal_operations.id"), nullable=False)
    date_operation = Column(DateTime, nullable=False)
    libelle_operation = Column(String, nullable=False)
    compte_debit = Column(String(50), nullable=False)  # 50 caractères max
    compte_credit = Column(String(50), nullable=False)  # 50 caractères max
    montant = Column(DECIMAL(15, 2), nullable=False)
    devise = Column(String(10), default="XOF")  # 10 caractères max
    reference_operation = Column(String(100), nullable=False)  # 100 caractères max
    module_origine = Column(String(100), nullable=False)  # 100 caractères max
    utilisateur_enregistrement_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)