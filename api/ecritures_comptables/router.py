from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import OperationJournal as OperationJournalModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..rbac_decorators import require_permission

router = APIRouter(tags=["Ecriture comptable"])
security = HTTPBearer()

# Endpoints pour les opérations de journal (écritures comptables)
@router.get("/", response_model=List[schemas.OperationJournalCreate],
           summary="Récupérer la liste des écritures comptables",
           description="Permet de récupérer la liste des écritures comptables avec pagination",
           dependencies=[Depends(require_permission("Module Écritures Comptables"))])
async def get_operations_journal(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    operations = db.query(OperationJournalModel).offset(skip).limit(limit).all()
    return operations

@router.post("/", response_model=schemas.OperationJournalCreate,
             summary="Créer une nouvelle écriture comptable",
             description="Permet de créer une nouvelle écriture comptable dans le journal",
             dependencies=[Depends(require_permission("Module Écritures Comptables"))])
async def create_operation_journal(
    operation: schemas.OperationJournalCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Créer l'enregistrement d'opération de journal
    db_operation = OperationJournalModel(
        journal_operations_id=operation.journal_operations_id,
        date_operation=operation.date_operation,
        libelle_operation=operation.libelle_operation,
        compte_debit=operation.compte_debit,
        compte_credit=operation.compte_credit,
        montant=operation.montant,
        devise=operation.devise,
        reference_operation=operation.reference_operation,
        module_origine=operation.module_origine,
        utilisateur_enregistrement_id=operation.utilisateur_enregistrement_id
    )

    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)

    return db_operation

@router.get("/{operation_id}", response_model=schemas.OperationJournalCreate,
           summary="Récupérer une écriture comptable par son ID",
           description="Permet de récupérer les détails d'une écriture comptable spécifique par son identifiant",
           dependencies=[Depends(require_permission("Module Écritures Comptables"))])
async def get_operation_journal_by_id(
    operation_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    operation = db.query(OperationJournalModel).filter(OperationJournalModel.id == operation_id).first()
    if not operation:
        raise HTTPException(status_code=404, detail="Opération de journal not found")
    return operation

@router.put("/{operation_id}", response_model=schemas.OperationJournalUpdate,
           summary="Mettre à jour une écriture comptable",
           description="Permet de modifier les informations d'une écriture comptable existante",
           dependencies=[Depends(require_permission("Module Écritures Comptables"))])
async def update_operation_journal(
    operation_id: str,  # UUID
    operation: schemas.OperationJournalUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_operation = db.query(OperationJournalModel).filter(OperationJournalModel.id == operation_id).first()
    if not db_operation:
        raise HTTPException(status_code=404, detail="Opération de journal not found")

    update_data = operation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_operation, field, value)

    db.commit()
    db.refresh(db_operation)
    return db_operation

@router.delete("/{operation_id}",
               summary="Supprimer une écriture comptable",
               description="Permet de supprimer une écriture comptable existante",
               dependencies=[Depends(require_permission("Module Écritures Comptables"))])
async def delete_operation_journal(
    operation_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    operation = db.query(OperationJournalModel).filter(OperationJournalModel.id == operation_id).first()
    if not operation:
        raise HTTPException(status_code=404, detail="Opération de journal not found")

    db.delete(operation)
    db.commit()
    return {"message": "Opération de journal deleted successfully"}