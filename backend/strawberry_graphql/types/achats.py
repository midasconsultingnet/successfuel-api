import strawberry
from typing import List, Optional
from datetime import datetime
from models.achats import (
    Achat as AchatModel,
    AchatDetail as AchatDetailModel,
    BonCommande as BonCommandeModel
)
from .base import BaseGraphQLType
from .structures import Fournisseur, Article, Station, Cuve

@strawberry.type
class Achat(BaseGraphQLType):
    fournisseur_id: Optional[str] = None
    date_achat: str
    total: float
    reference_facture: Optional[str] = None
    observation: Optional[str] = None
    type_achat: str = 'Produits'
    compagnie_id: str
    pays_id: Optional[str] = None
    devise_code: str = 'MGA'
    taux_change: float = 1.0
    journal_entry_id: Optional[str] = None
    statut: str = 'En attente de livraison'
    date_livraison: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: AchatModel):
        return cls(
            id=str(instance.id),
            fournisseur_id=str(instance.fournisseur_id) if instance.fournisseur_id else None,
            date_achat=instance.date_achat.isoformat() if instance.date_achat else None,
            total=float(instance.total) if instance.total else 0.0,
            reference_facture=instance.reference_facture,
            observation=instance.observation,
            type_achat=instance.type_achat,
            compagnie_id=str(instance.compagnie_id),
            pays_id=str(instance.pays_id) if instance.pays_id else None,
            devise_code=instance.devise_code,
            taux_change=float(instance.taux_change) if instance.taux_change else 1.0,
            journal_entry_id=str(instance.journal_entry_id) if instance.journal_entry_id else None,
            statut=instance.statut,
            date_livraison=instance.date_livraison.isoformat() if instance.date_livraison else None,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class AchatDetail:
    id: str
    achat_id: str
    article_id: str
    station_id: str
    cuve_id: Optional[str] = None
    quantite: float
    prix_unitaire: float
    statut: str = 'Actif'
    created_at: datetime
    
    @classmethod
    def from_instance(cls, instance: AchatDetailModel):
        return cls(
            id=str(instance.id),
            achat_id=str(instance.achat_id),
            article_id=str(instance.article_id),
            station_id=str(instance.station_id),
            cuve_id=str(instance.cuve_id) if instance.cuve_id else None,
            quantite=float(instance.quantite),
            prix_unitaire=float(instance.prix_unitaire),
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class BonCommande(BaseGraphQLType):
    numero_bon: str
    fournisseur_id: Optional[str] = None
    date_bon: str
    total: float
    observation: Optional[str] = None
    type_bon: str = 'Produits'
    compagnie_id: str
    statut: str = 'En cours'

    @classmethod
    def from_instance(cls, instance: BonCommandeModel):
        return cls(
            id=str(instance.id),
            numero_bon=instance.numero_bon,
            fournisseur_id=str(instance.fournisseur_id) if instance.fournisseur_id else None,
            date_bon=instance.date_bon.isoformat() if instance.date_bon else None,
            total=float(instance.total) if instance.total else 0.0,
            observation=instance.observation,
            type_bon=instance.type_bon,
            compagnie_id=str(instance.compagnie_id),
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )