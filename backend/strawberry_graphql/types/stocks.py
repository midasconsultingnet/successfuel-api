import strawberry
from typing import List, Optional
from datetime import datetime
from models.stocks import (
    MouvementStock as MouvementStockModel,
    MouvementStockDetail as MouvementStockDetailModel,
    Inventaire as InventaireModel,
    InventaireDetail as InventaireDetailModel,
    TransfertStock as TransfertStockModel,
    TransfertStockDetail as TransfertStockDetailModel
)
from .base import BaseGraphQLType

@strawberry.type
class MouvementStock(BaseGraphQLType):
    numero: str
    type_mouvement: str
    article_id: str
    station_id: str
    fournisseur_id: Optional[str] = None
    client_id: Optional[str] = None
    utilisateur_id: Optional[str] = None
    date_mouvement: str
    quantite: float
    prix_unitaire: float = 0.0
    valeur_totale: float = 0.0
    observation: Optional[str] = None
    reference_externe: Optional[str] = None
    compagnie_id: str
    pays_id: Optional[str] = None
    # Champs pour l'initialisation
    est_initial: Optional[bool] = False
    operation_initialisation_id: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: MouvementStockModel):
        return cls(
            id=str(instance.id),
            numero=instance.numero,
            type_mouvement=instance.type_mouvement,
            article_id=str(instance.article_id),
            station_id=str(instance.station_id),
            fournisseur_id=str(instance.fournisseur_id) if instance.fournisseur_id else None,
            client_id=str(instance.client_id) if instance.client_id else None,
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            date_mouvement=instance.date_mouvement.isoformat() if instance.date_mouvement else None,
            quantite=float(instance.quantite),
            prix_unitaire=float(instance.prix_unitaire) if instance.prix_unitaire else 0.0,
            valeur_totale=float(instance.valeur_totale) if instance.valeur_totale else 0.0,
            observation=instance.observation,
            reference_externe=instance.reference_externe,
            compagnie_id=str(instance.compagnie_id),
            pays_id=str(instance.pays_id) if instance.pays_id else None,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
            # Champs pour l'initialisation
            est_initial=getattr(instance, 'est_initial', False),
            operation_initialisation_id=str(instance.operation_initialisation_id) if hasattr(instance, 'operation_initialisation_id') and instance.operation_initialisation_id else None,
        )

@strawberry.type
class MouvementStockDetail:
    id: str
    mouvement_id: str
    article_id: str
    cuve_id: Optional[str] = None
    quantite: float
    prix_unitaire: float = 0.0
    valeur_totale: float = 0.0
    statut: str = 'Actif'
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: MouvementStockDetailModel):
        return cls(
            id=str(instance.id),
            mouvement_id=str(instance.mouvement_id),
            article_id=str(instance.article_id),
            cuve_id=str(instance.cuve_id) if instance.cuve_id else None,
            quantite=float(instance.quantite),
            prix_unitaire=float(instance.prix_unitaire) if instance.prix_unitaire else 0.0,
            valeur_totale=float(instance.valeur_totale) if instance.valeur_totale else 0.0,
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class Inventaire(BaseGraphQLType):
    numero: str
    date_inventaire: str
    heure_debut: str
    heure_fin: Optional[str] = None
    utilisateur_id: Optional[str] = None
    station_id: str
    type_inventaire: str = 'Complet'
    observation: Optional[str] = None
    statut: str = 'En cours'
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: InventaireModel):
        return cls(
            id=str(instance.id),
            numero=instance.numero,
            date_inventaire=instance.date_inventaire.isoformat() if instance.date_inventaire else None,
            heure_debut=instance.heure_debut.isoformat() if instance.heure_debut else None,
            heure_fin=instance.heure_fin.isoformat() if instance.heure_fin else None,
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            station_id=str(instance.station_id),
            type_inventaire=instance.type_inventaire,
            observation=instance.observation,
            statut=instance.statut,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class InventaireDetail:
    id: str
    inventaire_id: str
    article_id: str
    cuve_id: Optional[str] = None
    stock_theorique: float = 0.0
    stock_reel: float = 0.0
    ecart: float = 0.0
    observation: Optional[str] = None
    statut: str = 'Actif'
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: InventaireDetailModel):
        return cls(
            id=str(instance.id),
            inventaire_id=str(instance.inventaire_id),
            article_id=str(instance.article_id),
            cuve_id=str(instance.cuve_id) if instance.cuve_id else None,
            stock_theorique=float(instance.stock_theorique) if instance.stock_theorique else 0.0,
            stock_reel=float(instance.stock_reel) if instance.stock_reel else 0.0,
            ecart=float(instance.ecart) if instance.ecart else 0.0,
            observation=instance.observation,
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class TransfertStock(BaseGraphQLType):
    numero: str
    date_transfert: str
    heure_transfert: str
    utilisateur_id: Optional[str] = None
    station_origine_id: str
    station_destination_id: str
    observation: Optional[str] = None
    statut: str = 'En cours'
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: TransfertStockModel):
        return cls(
            id=str(instance.id),
            numero=instance.numero,
            date_transfert=instance.date_transfert.isoformat() if instance.date_transfert else None,
            heure_transfert=instance.heure_transfert.isoformat() if instance.heure_transfert else None,
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            station_origine_id=str(instance.station_origine_id),
            station_destination_id=str(instance.station_destination_id),
            observation=instance.observation,
            statut=instance.statut,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class TransfertStockDetail:
    id: str
    transfert_id: str
    article_id: str
    cuve_origine_id: Optional[str] = None
    cuve_destination_id: Optional[str] = None
    quantite: float
    prix_unitaire: float = 0.0
    valeur_totale: float = 0.0
    statut: str = 'Actif'
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: TransfertStockDetailModel):
        return cls(
            id=str(instance.id),
            transfert_id=str(instance.transfert_id),
            article_id=str(instance.article_id),
            cuve_origine_id=str(instance.cuve_origine_id) if instance.cuve_origine_id else None,
            cuve_destination_id=str(instance.cuve_destination_id) if instance.cuve_destination_id else None,
            quantite=float(instance.quantite),
            prix_unitaire=float(instance.prix_unitaire) if instance.prix_unitaire else 0.0,
            valeur_totale=float(instance.valeur_totale) if instance.valeur_totale else 0.0,
            statut=instance.statut,
            created_at=instance.created_at,
        )