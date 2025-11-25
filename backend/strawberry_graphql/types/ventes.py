import strawberry
from typing import List, Optional
from datetime import datetime
from models.ventes import (
    Vente as VenteModel,
    VenteDetail as VenteDetailModel,
    Reglement as ReglementModel
)
from .base import BaseGraphQLType

@strawberry.type
class Vente(BaseGraphQLType):
    numero: str
    client_id: Optional[str] = None
    utilisateur_id: str
    station_id: str
    date_vente: str
    heure_vente: str
    montant_total: float
    montant_encaisse: float = 0.0
    montant_rendu: float = 0.0
    type_paiement: str = 'Espèces'
    reference_paiement: Optional[str] = None
    observation: Optional[str] = None
    type_vente: str = 'Normale'
    compagnie_id: str
    pays_id: Optional[str] = None
    devise_code: str = 'MGA'
    taux_change: float = 1.0
    journal_entry_id: Optional[str] = None
    statut: str = 'Finalisée'

    @classmethod
    def from_instance(cls, instance: VenteModel):
        return cls(
            id=str(instance.id),
            numero=instance.numero,
            client_id=str(instance.client_id) if instance.client_id else None,
            utilisateur_id=str(instance.utilisateur_id),
            station_id=str(instance.station_id),
            date_vente=instance.date_vente.isoformat() if instance.date_vente else None,
            heure_vente=instance.heure_vente.isoformat() if instance.heure_vente else None,
            montant_total=float(instance.montant_total) if instance.montant_total else 0.0,
            montant_encaisse=float(instance.montant_encaisse) if instance.montant_encaisse else 0.0,
            montant_rendu=float(instance.montant_rendu) if instance.montant_rendu else 0.0,
            type_paiement=instance.type_paiement,
            reference_paiement=instance.reference_paiement,
            observation=instance.observation,
            type_vente=instance.type_vente,
            compagnie_id=str(instance.compagnie_id),
            pays_id=str(instance.pays_id) if instance.pays_id else None,
            devise_code=instance.devise_code,
            taux_change=float(instance.taux_change) if instance.taux_change else 1.0,
            journal_entry_id=str(instance.journal_entry_id) if instance.journal_entry_id else None,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class VenteDetail:
    id: str
    vente_id: str
    article_id: str
    pistolet_id: Optional[str] = None
    cuve_id: Optional[str] = None
    quantite: float
    prix_unitaire: float
    remise: float = 0.0
    taux_tva: float = 0.0
    montant_tva: float = 0.0
    montant_ht: float = 0.0
    montant_ttc: float = 0.0
    statut: str = 'Actif'
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: VenteDetailModel):
        return cls(
            id=str(instance.id),
            vente_id=str(instance.vente_id),
            article_id=str(instance.article_id),
            pistolet_id=str(instance.pistolet_id) if instance.pistolet_id else None,
            cuve_id=str(instance.cuve_id) if instance.cuve_id else None,
            quantite=float(instance.quantite),
            prix_unitaire=float(instance.prix_unitaire),
            remise=float(instance.remise) if instance.remise else 0.0,
            taux_tva=float(instance.taux_tva) if instance.taux_tva else 0.0,
            montant_tva=float(instance.montant_tva) if instance.montant_tva else 0.0,
            montant_ht=float(instance.montant_ht) if instance.montant_ht else 0.0,
            montant_ttc=float(instance.montant_ttc) if instance.montant_ttc else 0.0,
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class Reglement(BaseGraphQLType):
    numero: str
    client_id: Optional[str] = None
    utilisateur_id: str
    station_id: str
    date_reglement: str
    montant: float
    type_paiement: str
    reference_paiement: Optional[str] = None
    observation: Optional[str] = None
    compagnie_id: str
    pays_id: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: ReglementModel):
        return cls(
            id=str(instance.id),
            numero=instance.numero,
            client_id=str(instance.client_id) if instance.client_id else None,
            utilisateur_id=str(instance.utilisateur_id),
            station_id=str(instance.station_id),
            date_reglement=instance.date_reglement.isoformat() if instance.date_reglement else None,
            montant=float(instance.montant) if instance.montant else 0.0,
            type_paiement=instance.type_paiement,
            reference_paiement=instance.reference_paiement,
            observation=instance.observation,
            compagnie_id=str(instance.compagnie_id),
            pays_id=str(instance.pays_id) if instance.pays_id else None,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )