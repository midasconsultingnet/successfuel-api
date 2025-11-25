import strawberry
from typing import List, Optional
from datetime import datetime
from models.comptabilite import (
    JournalEntree as JournalEntreeModel,
    JournalLigne as JournalLigneModel,
    EtatStock as EtatStockModel,
    EtatCaisse as EtatCaisseModel,
    EtatComptable as EtatComptableModel
)
from .base import BaseGraphQLType

@strawberry.type
class JournalEntree(BaseGraphQLType):
    date_ecriture: str
    libelle: str
    type_operation: Optional[str] = None
    reference_operation: Optional[str] = None
    compagnie_id: str
    pays_id: Optional[str] = None
    created_by: Optional[str] = None
    est_valide: bool = False
    valide_par: Optional[str] = None
    date_validation: Optional[datetime] = None
    type_document_origine: Optional[str] = None
    document_origine_id: Optional[str] = None
    est_ouverture: bool = False
    bilan_initial_id: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: JournalEntreeModel):
        return cls(
            id=str(instance.id),
            date_ecriture=instance.date_ecriture.isoformat() if instance.date_ecriture else None,
            libelle=instance.libelle,
            type_operation=instance.type_operation,
            reference_operation=instance.reference_operation,
            compagnie_id=str(instance.compagnie_id),
            pays_id=str(instance.pays_id) if instance.pays_id else None,
            created_at=instance.created_at,
            statut=instance.statut,
            created_by=str(instance.created_by) if instance.created_by else None,
            est_valide=instance.est_valide,
            valide_par=str(instance.valide_par) if instance.valide_par else None,
            date_validation=instance.date_validation,
            type_document_origine=instance.type_document_origine,
            document_origine_id=str(instance.document_origine_id) if instance.document_origine_id else None,
            est_ouverture=instance.est_ouverture,
            bilan_initial_id=str(instance.bilan_initial_id) if instance.bilan_initial_id else None,
            updated_at=instance.updated_at,
        )

@strawberry.type
class JournalLigne:
    id: str
    entry_id: str
    compte_num: Optional[str] = None
    compte_id: Optional[str] = None
    debit: float = 0.0
    credit: float = 0.0
    sens: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: JournalLigneModel):
        return cls(
            id=str(instance.id),
            entry_id=str(instance.entry_id),
            compte_num=instance.compte_num,
            compte_id=str(instance.compte_id) if instance.compte_id else None,
            debit=float(instance.debit) if instance.debit else 0.0,
            credit=float(instance.credit) if instance.credit else 0.0,
            sens=instance.sens,
            created_at=instance.created_at,
        )

@strawberry.type
class EtatStock:
    id: str
    date_etat: str
    article_id: str
    station_id: str
    stock_initial: float = 0.0
    entrees: float = 0.0
    sorties: float = 0.0
    stock_final: float = 0.0
    valeur_stock: float = 0.0
    observation: Optional[str] = None
    statut: str = 'Actif'
    compagnie_id: str
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: EtatStockModel):
        return cls(
            id=str(instance.id),
            date_etat=instance.date_etat.isoformat() if instance.date_etat else None,
            article_id=str(instance.article_id),
            station_id=str(instance.station_id),
            stock_initial=float(instance.stock_initial) if instance.stock_initial else 0.0,
            entrees=float(instance.entrees) if instance.entrees else 0.0,
            sorties=float(instance.sorties) if instance.sorties else 0.0,
            stock_final=float(instance.stock_final) if instance.stock_final else 0.0,
            valeur_stock=float(instance.valeur_stock) if instance.valeur_stock else 0.0,
            observation=instance.observation,
            statut=instance.statut,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
        )

@strawberry.type
class EtatCaisse:
    id: str
    date_etat: str
    tresorerie_id: str
    solde_initial: float = 0.0
    encaissements: float = 0.0
    decaissements: float = 0.0
    solde_final: float = 0.0
    ecart: float = 0.0
    observation: Optional[str] = None
    statut: str = 'Actif'
    compagnie_id: str
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: EtatCaisseModel):
        return cls(
            id=str(instance.id),
            date_etat=instance.date_etat.isoformat() if instance.date_etat else None,
            tresorerie_id=str(instance.tresorerie_id),
            solde_initial=float(instance.solde_initial) if instance.solde_initial else 0.0,
            encaissements=float(instance.encaissements) if instance.encaissements else 0.0,
            decaissements=float(instance.decaissements) if instance.decaissements else 0.0,
            solde_final=float(instance.solde_final) if instance.solde_final else 0.0,
            ecart=float(instance.ecart) if instance.ecart else 0.0,
            observation=instance.observation,
            statut=instance.statut,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
        )

@strawberry.type
class EtatComptable:
    id: str
    date_etat: str
    compte_id: str
    solde_initial: float = 0.0
    debit_periode: float = 0.0
    credit_periode: float = 0.0
    solde_final: float = 0.0
    observation: Optional[str] = None
    statut: str = 'Actif'
    compagnie_id: str
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: EtatComptableModel):
        return cls(
            id=str(instance.id),
            date_etat=instance.date_etat.isoformat() if instance.date_etat else None,
            compte_id=str(instance.compte_id),
            solde_initial=float(instance.solde_initial) if instance.solde_initial else 0.0,
            debit_periode=float(instance.debit_periode) if instance.debit_periode else 0.0,
            credit_periode=float(instance.credit_periode) if instance.credit_periode else 0.0,
            solde_final=float(instance.solde_final) if instance.solde_final else 0.0,
            observation=instance.observation,
            statut=instance.statut,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
        )