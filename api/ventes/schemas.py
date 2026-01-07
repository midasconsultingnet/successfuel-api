from pydantic import BaseModel, Field
from typing import Optional, List, Union
from decimal import Decimal
from datetime import datetime
import uuid

class VenteDetailCreate(BaseModel):
    produit_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique du produit vendu",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    quantite: int = Field(
        ...,
        ge=1,
        description="Quantité du produit vendu",
        example=2
    )
    prix_unitaire: float = Field(
        ...,
        ge=0,
        description="Prix unitaire du produit",
        example=1500.0
    )
    montant: float = Field(
        ...,
        ge=0,
        description="Montant total pour cette ligne de vente",
        example=3000.0
    )
    remise: Optional[float] = Field(
        0,
        ge=0,
        description="Remise appliquée sur ce produit (en pourcentage ou montant)",
        example=5.0
    )

class VenteDetailUpdate(BaseModel):
    quantite: Optional[int] = Field(
        None,
        ge=1,
        description="Quantité du produit vendu",
        example=2
    )
    prix_unitaire: Optional[float] = Field(
        None,
        ge=0,
        description="Prix unitaire du produit",
        example=1500.0
    )
    montant: Optional[float] = Field(
        None,
        ge=0,
        description="Montant total pour cette ligne de vente",
        example=3000.0
    )
    remise: Optional[float] = Field(
        None,
        ge=0,
        description="Remise appliquée sur ce produit (en pourcentage ou montant)",
        example=5.0
    )

class VenteCreate(BaseModel):
    client_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant unique du client (facultatif pour les ventes au comptant)",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    date: datetime = Field(
        ...,
        description="Date et heure de la vente",
        example="2023-10-15T09:30:00"
    )
    statut: str = Field(
        ...,
        description="Statut de la vente (en_cours, terminee, annulee)",
        example="en_cours"
    )
    type_vente: str = Field(
        ...,
        description="Type de vente (produit, service, hybride)",
        example="produit"
    )
    informations: Optional[str] = Field(
        None,
        description="Informations supplémentaires au format JSON",
        example='{"numero_bl": "BL-2023-001", "numero_facture": "FAC-2023-001"}'
    )
    tresorerie_id: uuid.UUID = Field(
        ...,
        description="Identifiant de la trésorerie utilisée pour la vente",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    details: List[VenteDetailCreate] = Field(
        ...,
        description="Détails des produits vendus dans cette vente"
    )

    class Config:
        from_attributes = True

class VenteUpdate(BaseModel):
    client_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant unique du client (facultatif pour les ventes au comptant)",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    date: Optional[datetime] = Field(
        None,
        description="Date et heure de la vente",
        example="2023-10-15T09:30:00"
    )
    montant_total: Optional[float] = Field(
        None,
        ge=0,
        description="Montant total de la vente",
        example=5000.0
    )
    statut: Optional[str] = Field(
        None,
        description="Statut de la vente (en_cours, terminee, annulee)",
        example="terminee"
    )
    type_vente: Optional[str] = Field(
        None,
        description="Type de vente (produit, service, hybride)",
        example="produit"
    )
    informations: Optional[str] = Field(
        None,
        description="Informations supplémentaires au format JSON",
        example='{"numero_bl": "BL-2023-001", "numero_facture": "FAC-2023-001"}'
    )
    tresorerie_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant de la trésorerie utilisée pour la vente",
        example="123e4567-e89b-12d3-a456-426614174002"
    )

    class Config:
        from_attributes = True

# Schémas pour les ventes de carburant
class VenteCarburantCreate(BaseModel):
    station_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la station-service où la vente a eu lieu",
        example="123e4567-e89b-12d3-a456-426614174003"
    )
    cuve_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la cuve d'où le carburant a été prélevé",
        example="123e4567-e89b-12d3-a456-426614174004"
    )
    pistolet_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique du pistolet de distribution utilisé",
        example="123e4567-e89b-12d3-a456-426614174005"
    )
    tresorerie_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant de la trésorerie utilisée pour enregistrer le paiement",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    carburant_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant du type de carburant vendu",
        example="123e4567-e89b-12d3-a456-426614174006"
    )
    quantite_vendue: float = Field(
        ...,
        gt=0,
        description="Quantité de carburant vendue en litres",
        example=25.0
    )
    prix_unitaire: Optional[float] = Field(
        None,
        ge=0,
        description="Prix unitaire du carburant en devise locale par litre",
        example=1.25
    )
    montant_total: Optional[float] = Field(
        None,
        ge=0,
        description="Montant total de la vente",
        example=31.25
    )
    date_vente: datetime = Field(
        ...,
        description="Date et heure de la vente",
        example="2023-10-15T09:30:00"
    )
    index_initial: Union[float, Decimal] = Field(
        ...,
        ge=0,
        description="Index initial du pistolet avant la vente",
        example=1250.0
    )
    index_final: Union[float, Decimal] = Field(
        ...,
        ge=0,
        description="Index final du pistolet après la vente",
        example=1275.0
    )
    quantite_mesuree: Optional[Union[float, Decimal]] = Field(
        None,
        ge=0,
        description="Quantité mesurée basée sur la différence des index du pistolet",
        example=25.0
    )
    ecart_quantite: Optional[Union[float, Decimal]] = Field(
        None,
        description="Différence entre la quantité vendue et la quantité mesurée",
        example=0.0
    )
    besoin_compensation: Optional[bool] = Field(
        False,
        description="Indique si une compensation est nécessaire en cas d'écart significatif"
    )
    compensation_id: Optional[uuid.UUID] = Field(
        None,
        description="Référence à l'avoir de compensation si nécessaire",
        example="123e4567-e89b-12d3-a456-426614174007"
    )
    pompiste: str = Field(
        ...,
        description="Nom du pompiste qui a effectué la vente",
        example="M. Diop"
    )
    qualite_marshalle_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant du contrôleur qualité qui a vérifié la transaction",
        example="123e4567-e89b-12d3-a456-426614174008"
    )
    montant_paye: Optional[float] = Field(
        0,
        ge=0,
        description="Montant effectivement payé par le client",
        example=31.25
    )
    mode_paiement: Optional[str] = Field(
        None,
        description="Mode de paiement utilisé (espèce, chèque, carte crédit, note de crédit, crédit client)",
        example="espèce"
    )
    utilisateur_id: uuid.UUID = Field(
        ...,
        description="Identifiant de l'utilisateur qui a enregistré la vente",
        example="123e4567-e89b-12d3-a456-426614174009"
    )

    class Config:
        from_attributes = True

class VenteCarburantUpdate(BaseModel):
    montant_paye: Optional[float] = Field(
        None,
        ge=0,
        description="Montant effectivement payé par le client",
        example=31.25
    )
    mode_paiement: Optional[str] = Field(
        None,
        description="Mode de paiement utilisé (espèce, chèque, carte crédit, note de crédit, crédit client)",
        example="espèce"
    )
    statut: Optional[str] = Field(
        None,
        description="Statut de la vente (enregistrée, validée, annulée)",
        example="validée"
    )
    numero_piece_comptable: Optional[str] = Field(
        None,
        description="Numéro de pièce comptable associé à la vente",
        example="VTC-2023-10-001"
    )
    tresorerie_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant de la trésorerie utilisée pour enregistrer le paiement",
        example="123e4567-e89b-12d3-a456-426614174002"
    )

    class Config:
        from_attributes = True

class CreanceEmployeCreate(BaseModel):
    vente_carburant_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant de la vente de carburant liée à cette créance",
        example="123e4567-e89b-12d3-a456-426614174010"
    )
    pompiste: str = Field(
        ...,
        description="Nom du pompiste concerné par la créance",
        example="M. Diop"
    )
    montant_du: float = Field(
        ...,
        ge=0,
        description="Montant total dû par l'employé",
        example=5000.0
    )
    montant_paye: Optional[float] = Field(
        0,
        ge=0,
        description="Montant déjà payé par l'employé",
        example=2000.0
    )
    created_at: datetime = Field(
        ...,
        description="Date de création de la créance",
        example="2023-10-15T09:30:00"
    )
    date_echeance: Optional[datetime] = Field(
        None,
        description="Date d'échéance du paiement de la créance",
        example="2023-11-15T09:30:00"
    )
    utilisateur_gestion_id: uuid.UUID = Field(
        ...,
        description="Identifiant de l'utilisateur chargé de la gestion de cette créance",
        example="123e4567-e89b-12d3-a456-426614174009"
    )

    class Config:
        from_attributes = True

class CreanceEmployeUpdate(BaseModel):
    montant_paye: Optional[float] = Field(
        None,
        ge=0,
        description="Montant payé par l'employé",
        example=1000.0
    )
    date_echeance: Optional[datetime] = Field(
        None,
        description="Date d'échéance du paiement de la créance",
        example="2023-11-15T09:30:00"
    )
    statut: Optional[str] = Field(
        None,
        description="Statut de la créance (en_cours, payé, partiellement_payé)",
        example="partiellement_payé"
    )

    class Config:
        from_attributes = True

# Schémas de réponse pour la vente de produits
class VenteResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la vente",
        example="123e4567-e89b-12d3-a456-426614174011"
    )
    client_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant unique du client (facultatif pour les ventes au comptant)",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    date: datetime = Field(
        ...,
        description="Date et heure de la vente",
        example="2023-10-15T09:30:00"
    )
    montant_total: float = Field(
        ...,
        ge=0,
        description="Montant total de la vente",
        example=5000.0
    )
    statut: str = Field(
        ...,
        description="Statut de la vente (en_cours, terminee, annulee)",
        example="en_cours"
    )
    type_vente: str = Field(
        ...,
        description="Type de vente (produit, service, hybride)",
        example="produit"
    )
    informations: Optional[str] = Field(
        None,
        description="Informations supplémentaires au format JSON",
        example='{"numero_bl": "BL-2023-001", "numero_facture": "FAC-2023-001"}'
    )
    tresorerie_id: uuid.UUID = Field(
        ...,
        description="Identifiant de la trésorerie utilisée pour la vente",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    utilisateur_id: uuid.UUID = Field(
        ...,
        description="Identifiant de l'utilisateur qui a enregistré la vente",
        example="123e4567-e89b-12d3-a456-426614174009"
    )
    station_id: uuid.UUID = Field(
        ...,
        description="Identifiant de la station où la vente a eu lieu",
        example="123e4567-e89b-12d3-a456-426614174003"
    )
    compagnie_id: uuid.UUID = Field(
        ...,
        description="Identifiant de la compagnie associée à la vente",
        example="123e4567-e89b-12d3-a456-426614174012"
    )
    created_at: datetime = Field(
        ...,
        description="Date de création de la vente",
        example="2023-10-15T09:30:00"
    )
    updated_at: datetime = Field(
        ...,
        description="Date de dernière mise à jour de la vente",
        example="2023-10-15T09:30:00"
    )

    class Config:
        from_attributes = True

class VenteDetailResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Identifiant unique du détail de la vente",
        example="123e4567-e89b-12d3-a456-426614174013"
    )
    vente_id: uuid.UUID = Field(
        ...,
        description="Identifiant de la vente liée à ce détail",
        example="123e4567-e89b-12d3-a456-426614174011"
    )
    produit_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique du produit vendu",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    quantite: int = Field(
        ...,
        ge=1,
        description="Quantité du produit vendu",
        example=2
    )
    prix_unitaire: float = Field(
        ...,
        ge=0,
        description="Prix unitaire du produit",
        example=1500.0
    )
    montant: float = Field(
        ...,
        ge=0,
        description="Montant total pour cette ligne de vente",
        example=3000.0
    )
    remise: Optional[float] = Field(
        0,
        ge=0,
        description="Remise appliquée sur ce produit (en pourcentage ou montant)",
        example=5.0
    )
    created_at: datetime = Field(
        ...,
        description="Date de création du détail de vente",
        example="2023-10-15T09:30:00"
    )
    updated_at: datetime = Field(
        ...,
        description="Date de dernière mise à jour du détail de vente",
        example="2023-10-15T09:30:00"
    )

    class Config:
        from_attributes = True


# Schémas de réponse pour la vente de carburant
class VenteCarburantResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la vente de carburant",
        example="123e4567-e89b-12d3-a456-426614174014"
    )
    station_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la station-service où la vente a eu lieu",
        example="123e4567-e89b-12d3-a456-426614174003"
    )
    cuve_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la cuve d'où le carburant a été prélevé",
        example="123e4567-e89b-12d3-a456-426614174004"
    )
    pistolet_id: uuid.UUID = Field(
        ...,
        description="Identifiant unique du pistolet de distribution utilisé",
        example="123e4567-e89b-12d3-a456-426614174005"
    )
    tresorerie_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant de la trésorerie utilisée pour enregistrer le paiement",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    carburant_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant du type de carburant vendu",
        example="123e4567-e89b-12d3-a456-426614174006"
    )
    quantite_vendue: float = Field(
        ...,
        gt=0,
        description="Quantité de carburant vendue en litres",
        example=25.0
    )
    prix_unitaire: Optional[float] = Field(
        None,
        ge=0,
        description="Prix unitaire du carburant en devise locale par litre",
        example=1.25
    )
    montant_total: Optional[float] = Field(
        None,
        ge=0,
        description="Montant total de la vente",
        example=31.25
    )
    date_vente: datetime = Field(
        ...,
        description="Date et heure de la vente",
        example="2023-10-15T09:30:00"
    )
    index_initial: Union[float, Decimal] = Field(
        ...,
        ge=0,
        description="Index initial du pistolet avant la vente",
        example=1250.0
    )
    index_final: Union[float, Decimal] = Field(
        ...,
        ge=0,
        description="Index final du pistolet après la vente",
        example=1275.0
    )
    quantite_mesuree: Optional[Union[float, Decimal]] = Field(
        None,
        ge=0,
        description="Quantité mesurée basée sur la différence des index du pistolet",
        example=25.0
    )
    ecart_quantite: Optional[Union[float, Decimal]] = Field(
        None,
        description="Différence entre la quantité vendue et la quantité mesurée",
        example=0.0
    )
    besoin_compensation: Optional[bool] = Field(
        False,
        description="Indique si une compensation est nécessaire en cas d'écart significatif"
    )
    compensation_id: Optional[uuid.UUID] = Field(
        None,
        description="Référence à l'avoir de compensation si nécessaire",
        example="123e4567-e89b-12d3-a456-426614174007"
    )
    pompiste: str = Field(
        ...,
        description="Nom du pompiste qui a effectué la vente",
        example="M. Diop"
    )
    qualite_marshalle_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant du contrôleur qualité qui a vérifié la transaction",
        example="123e4567-e89b-12d3-a456-426614174008"
    )
    montant_paye: Optional[float] = Field(
        0,
        ge=0,
        description="Montant effectivement payé par le client",
        example=31.25
    )
    mode_paiement: Optional[str] = Field(
        None,
        description="Mode de paiement utilisé (espèce, chèque, carte crédit, note de crédit, crédit client)",
        example="espèce"
    )
    utilisateur_id: uuid.UUID = Field(
        ...,
        description="Identifiant de l'utilisateur qui a enregistré la vente",
        example="123e4567-e89b-12d3-a456-426614174009"
    )
    created_at: datetime = Field(
        ...,
        description="Date de création de la vente de carburant",
        example="2023-10-15T09:30:00"
    )
    updated_at: datetime = Field(
        ...,
        description="Date de dernière mise à jour de la vente de carburant",
        example="2023-10-15T09:30:00"
    )

    class Config:
        from_attributes = True


# Schémas de réponse pour les créances employés
class CreanceEmployeResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="Identifiant unique de la créance d'employé",
        example="123e4567-e89b-12d3-a456-426614174015"
    )
    vente_carburant_id: Optional[uuid.UUID] = Field(
        None,
        description="Identifiant de la vente de carburant liée à cette créance",
        example="123e4567-e89b-12d3-a456-426614174010"
    )
    pompiste: str = Field(
        ...,
        description="Nom du pompiste concerné par la créance",
        example="M. Diop"
    )
    montant_du: float = Field(
        ...,
        ge=0,
        description="Montant total dû par l'employé",
        example=5000.0
    )
    montant_paye: Optional[float] = Field(
        0,
        ge=0,
        description="Montant déjà payé par l'employé",
        example=2000.0
    )
    created_at: datetime = Field(
        ...,
        description="Date de création de la créance",
        example="2023-10-15T09:30:00"
    )
    date_echeance: Optional[datetime] = Field(
        None,
        description="Date d'échéance du paiement de la créance",
        example="2023-11-15T09:30:00"
    )
    utilisateur_gestion_id: uuid.UUID = Field(
        ...,
        description="Identifiant de l'utilisateur chargé de la gestion de cette créance",
        example="123e4567-e89b-12d3-a456-426614174009"
    )
    statut: str = Field(
        "en_cours",
        description="Statut de la créance (en_cours, payé, partiellement_payé)",
        example="en_cours"
    )

    class Config:
        from_attributes = True