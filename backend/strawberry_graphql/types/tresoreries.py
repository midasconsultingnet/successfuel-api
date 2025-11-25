import strawberry
from typing import List, Optional
from datetime import datetime
from models.tresoreries import (
    MouvementTresorerie as MouvementTresorerieModel,
    MouvementTresorerieDetail as MouvementTresorerieDetailModel,
    BilanInitial as BilanInitialModel,
    Journal as JournalModel
)
from .base import BaseGraphQLType

@strawberry.type
class MouvementTresorerie(BaseGraphQLType):
    numero: str
    type_mouvement: str
    tresorerie_id: str
    utilisateur_id: Optional[str] = None
    date_mouvement: str
    heure_mouvement: str
    montant: float
    devise_montant: str = 'MGA'
    taux_change: float = 1.0
    montant_devise: float = 0.0
    tiers_id: Optional[str] = None
    type_tiers: Optional[str] = None
    reference_externe: Optional[str] = None
    observation: Optional[str] = None
    compagnie_id: str
    pays_id: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: MouvementTresorerieModel):
        return cls(
            id=str(instance.id),
            numero=instance.numero,
            type_mouvement=instance.type_mouvement,
            tresorerie_id=str(instance.tresorerie_id),
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            date_mouvement=instance.date_mouvement.isoformat() if instance.date_mouvement else None,
            heure_mouvement=instance.heure_mouvement.isoformat() if instance.heure_mouvement else None,
            montant=float(instance.montant),
            devise_montant=instance.devise_montant,
            taux_change=float(instance.taux_change) if instance.taux_change else 1.0,
            montant_devise=float(instance.montant_devise) if instance.montant_devise else 0.0,
            tiers_id=str(instance.tiers_id) if instance.tiers_id else None,
            type_tiers=instance.type_tiers,
            reference_externe=instance.reference_externe,
            observation=instance.observation,
            compagnie_id=str(instance.compagnie_id),
            pays_id=str(instance.pays_id) if instance.pays_id else None,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class MouvementTresorerieDetail:
    id: str
    mouvement_id: str
    compte_comptable_id: Optional[str] = None
    type_operation: Optional[str] = None
    montant: float
    statut: str = 'Actif'
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: MouvementTresorerieDetailModel):
        return cls(
            id=str(instance.id),
            mouvement_id=str(instance.mouvement_id),
            compte_comptable_id=str(instance.compte_comptable_id) if instance.compte_comptable_id else None,
            type_operation=instance.type_operation,
            montant=float(instance.montant),
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class BilanInitial(BaseGraphQLType):
    date_bilan: str
    utilisateur_id: Optional[str] = None
    observation: Optional[str] = None
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: BilanInitialModel):
        return cls(
            id=str(instance.id),
            date_bilan=instance.date_bilan.isoformat() if instance.date_bilan else None,
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            observation=instance.observation,
            statut=instance.statut,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Journal(BaseGraphQLType):
    code: str
    libelle: str
    type_journal: str
    observation: Optional[str] = None
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: JournalModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            libelle=instance.libelle,
            type_journal=instance.type_journal,
            observation=instance.observation,
            statut=instance.statut,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )