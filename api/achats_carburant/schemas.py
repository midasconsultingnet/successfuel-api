from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class AchatCarburantCreate(BaseModel):
    """Schéma pour créer un achat de carburant."""
    fournisseur_id: UUID = Field(
        ...,
        description="Identifiant unique du fournisseur",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    date_achat: datetime = Field(
        ...,
        description="Date de l'achat au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )
    autres_infos: Optional[Dict[str, Any]] = Field(
        None,
        description="Informations supplémentaires au format JSON (remplace numero_bl)",
        example={"numero_bl": "BL-2023-12-001", "temperature": 15.5, "densite": 0.835}
    )
    numero_facture: Optional[str] = Field(
        None,
        description="Numéro de la facture",
        example="FAC-2023-12-001"
    )
    montant_total: float = Field(
        ...,
        description="Montant total de l'achat",
        ge=0,
        example=2500000.0
    )
    compagnie_id: UUID = Field(
        ...,
        description="Identifiant unique de la compagnie",
        example="123e4567-e89b-12d3-a456-426614174001"
    )

class AchatCarburantDetailCreate(BaseModel):
    """Schéma pour créer un détail d'achat de carburant."""
    station_id: UUID = Field(
        ...,
        description="Identifiant unique de la station de destination",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    carburant_id: UUID = Field(
        ...,
        description="Identifiant du type de carburant",
        example="123e4567-e89b-12d3-a456-426614174004"
    )
    quantite: float = Field(
        ...,
        description="Quantité de carburant",
        ge=0,
        example=1000.0
    )

class AchatCarburantReglementCreate(BaseModel):
    """Schéma pour créer un règlement d'achat de carburant."""
    date: datetime = Field(
        ...,
        description="Date du paiement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2025-10-18T00:00:00.000000"
    )
    montant: float = Field(
        ...,
        description="Montant du paiement",
        ge=0,
        example=2500000.0
    )
    mode_paiement: str = Field(
        ...,
        description="Mode de paiement (espèces, chèque, virement, carte_bancaire, etc.)",
        example="cheque"
    )
    reference: Optional[str] = Field(
        None,
        description="Référence du paiement (numéro de chèque, référence de virement, etc.)",
        example="12345678"
    )
    tresorerie_station_id: UUID = Field(
        ...,
        description="Identifiant de la trésorerie station concernée par le paiement",
        example="4c610b99-0e5d-43a4-ad2e-c9b7d3fce51d"
    )

class AchatCarburantCreateWithDetails(BaseModel):
    """Schéma pour créer un achat de carburant avec ses détails et paiements."""
    fournisseur_id: UUID = Field(
        ...,
        description="Identifiant unique du fournisseur",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    date_achat: datetime = Field(
        ...,
        description="Date de l'achat au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )
    numero_bl: Optional[str] = Field(
        None,
        description="Numéro de bon de livraison",
        example="BL-2023-12-001"
    )
    numero_facture: Optional[str] = Field(
        None,
        description="Numéro de la facture",
        example="FAC-2023-12-001"
    )
    montant_total: float = Field(
        ...,
        description="Montant total de l'achat",
        ge=0,
        example=2500000.0
    )
    compagnie_id: Optional[UUID] = Field(
        None,
        description="Identifiant unique de la compagnie (récupéré automatiquement à partir de l'utilisateur connecté)",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    details: List[AchatCarburantDetailCreate] = Field(
        ...,
        description="Détails des produits achetés"
    )
    reglements: List[AchatCarburantReglementCreate] = Field(
        ...,
        description="Paiements associés à l'achat"
    )

    def to_achat_carburant_create(self, utilisateur_id: UUID) -> 'AchatCarburantCreate':
        """Convertir en AchatCarburantCreate."""
        # Ajouter numero_bl dans autres_infos
        autres_infos = {"numero_bl": self.numero_bl} if self.numero_bl else None
        return AchatCarburantCreate(
            fournisseur_id=self.fournisseur_id,
            date_achat=self.date_achat,
            autres_infos=autres_infos,
            numero_facture=self.numero_facture,
            montant_total=self.montant_total,
            compagnie_id=self.compagnie_id  # Le service récupère automatiquement la compagnie de l'utilisateur
        )

class AchatCarburantUpdate(BaseModel):
    """Schéma pour la mise à jour d'un achat de carburant."""
    autres_infos: Optional[Dict[str, Any]] = Field(
        None,
        description="Informations supplémentaires au format JSON (remplace numero_bl)",
        example={"numero_bl": "BL-2023-12-001", "temperature": 15.5, "densite": 0.835}
    )
    numero_facture: Optional[str] = Field(
        None,
        description="Numéro de la facture",
        example="FAC-2023-12-001"
    )
    montant_total: Optional[float] = Field(
        None,
        description="Montant total de l'achat",
        ge=0,
        example=2500000.0
    )
    statut: Optional[str] = Field(
        None,
        description="Statut de l'achat (brouillon, validé, facturé, annulé)",
        example="validé"
    )  # brouillon, validé, facturé, annulé

class LigneAchatCarburantCreate(BaseModel):
    """Schéma pour créer une ligne d'achat de carburant."""
    achat_carburant_id: UUID = Field(
        ...,
        description="Identifiant de l'achat de carburant auquel la ligne est associée",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    carburant_id: UUID = Field(
        ...,
        description="Identifiant du type de carburant",
        example="123e4567-e89b-12d3-a456-426614174004"
    )  # UUID
    quantite: float = Field(
        ...,
        description="Quantité de carburant",
        ge=0,
        example=1000.0
    )
    prix_unitaire: float = Field(
        ...,
        description="Prix unitaire du carburant",
        ge=0,
        example=1500.0
    )
    montant: float = Field(
        ...,
        description="Montant total pour cette ligne",
        ge=0,
        example=1500000.0
    )
    station_id: UUID = Field(
        ...,
        description="Identifiant unique de la station de destination",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID

class LigneAchatCarburantUpdate(BaseModel):
    """Schéma pour la mise à jour d'une ligne d'achat de carburant."""
    quantite: Optional[float] = Field(
        None,
        description="Quantité de carburant",
        ge=0,
        example=1000.0
    )
    prix_unitaire: Optional[float] = Field(
        None,
        description="Prix unitaire du carburant",
        ge=0,
        example=1500.0
    )
    montant: Optional[float] = Field(
        None,
        description="Montant total pour cette ligne",
        ge=0,
        example=1500000.0
    )

class CompensationFinanciereCreate(BaseModel):
    """Schéma pour créer une compensation financière."""
    achat_carburant_id: UUID = Field(
        ...,
        description="Identifiant de l'achat de carburant concerné par la compensation",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    type_compensation: str = Field(
        ...,
        description="Type de compensation ('avoir_reçu' ou 'avoir_dû')",
        example="avoir_reçu"
    )  # "avoir_reçu", "avoir_dû"
    quantite_theorique: float = Field(
        ...,
        description="Quantité théorique prévue dans l'achat",
        ge=0,
        example=1000.0
    )
    quantite_reelle: float = Field(
        ...,
        description="Quantité réellement livrée",
        ge=0,
        example=950.0
    )
    difference: float = Field(
        ...,
        description="Différence entre la quantité réelle et la quantité théorique",
        example=50.0
    )
    montant_compensation: float = Field(
        ...,
        description="Montant de la compensation",
        ge=0,
        example=75000.0
    )
    motif: Optional[str] = Field(
        None,
        description="Motif de la compensation",
        example="Perte en transit"
    )

class CompensationFinanciereUpdate(BaseModel):
    """Schéma pour la mise à jour d'une compensation financière."""
    statut: Optional[str] = Field(
        None,
        description="Statut de la compensation (émis, utilisé, partiellement_utilisé, expiré)",
        example="émis"
    )  # émis, utilisé, partiellement_utilisé, expiré
    motif: Optional[str] = Field(
        None,
        description="Motif de la compensation",
        example="Perte en transit"
    )

class AvoirCompensationCreate(BaseModel):
    """Schéma pour créer un avoir de compensation."""
    compensation_financiere_id: UUID = Field(
        ...,
        description="Identifiant de la compensation financière à laquelle l'avoir est lié",
        example="123e4567-e89b-12d3-a456-426614174006"
    )  # UUID
    tiers_id: UUID = Field(
        ...,
        description="Identifiant du tiers (fournisseur ou client) concerné",
        example="123e4567-e89b-12d3-a456-426614174007"
    )  # UUID
    montant: float = Field(
        ...,
        description="Montant de l'avoir",
        ge=0,
        example=75000.0
    )
    motif: str = Field(
        ...,
        description="Motif de l'avoir de compensation",
        example="Perte en transit"
    )

class PaiementAchatCarburantCreate(BaseModel):
    """Schéma pour créer un paiement d'achat de carburant."""
    achat_carburant_id: UUID = Field(
        ...,
        description="Identifiant de l'achat de carburant concerné par le paiement",
        example="123e4567-e89b-12d3-a456-426614174003"
    )
    date_paiement: datetime = Field(
        ...,
        description="Date du paiement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-18T10:30:00.000000"
    )
    montant: float = Field(
        ...,
        description="Montant du paiement",
        ge=0,
        example=2500000.0
    )
    mode_paiement: str = Field(
        ...,
        description="Mode de paiement (espèces, chèque, virement, carte_bancaire, etc.)",
        example="virement"
    )
    tresorerie_station_id: UUID = Field(
        ...,
        description="Identifiant de la trésorerie station concernée par le paiement",
        example="123e4567-e89b-12d3-a456-426614174009"
    )

class PaiementAchatCarburantUpdate(BaseModel):
    """Schéma pour la mise à jour d'un paiement d'achat de carburant."""
    date_paiement: Optional[datetime] = Field(
        None,
        description="Date du paiement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-18T10:30:00.000000"
    )
    montant: Optional[float] = Field(
        None,
        description="Montant du paiement",
        ge=0,
        example=2500000.0
    )
    mode_paiement: Optional[str] = Field(
        None,
        description="Mode de paiement (espèces, chèque, virement, carte_bancaire, etc.)",
        example="virement"
    )
    tresorerie_station_id: Optional[UUID] = Field(
        None,
        description="Identifiant de la trésorerie station concernée par le paiement",
        example="123e4567-e89b-12d3-a456-426614174009"
    )
    statut: Optional[str] = Field(
        None,
        description="Statut du paiement (enregistré, validé, annulé)",
        example="validé"
    )


class AchatCarburantResponse(BaseModel):
    """Schéma pour la réponse d'un achat de carburant."""
    id: UUID = Field(
        ...,
        description="Identifiant unique de l'achat de carburant",
        example="123e4567-e89b-12d3-a456-426614174008"
    )  # UUID
    fournisseur_id: UUID = Field(
        ...,
        description="Identifiant unique du fournisseur",
        example="123e4567-e89b-12d3-a456-426614174000"
    )  # UUID
    date_achat: datetime = Field(
        ...,
        description="Date de l'achat au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-17T10:30:00.000000"
    )
    autres_infos: Optional[Dict[str, Any]] = Field(
        None,
        description="Informations supplémentaires au format JSON (remplace numero_bl)",
        example={"numero_bl": "BL-2023-12-001", "temperature": 15.5, "densite": 0.835}
    )
    numero_facture: Optional[str] = Field(
        None,
        description="Numéro de la facture",
        example="FAC-2023-12-001"
    )
    montant_total: float = Field(
        ...,
        description="Montant total de l'achat",
        ge=0,
        example=2500000.0
    )
    statut: str = Field(
        "brouillon",
        description="Statut de l'achat (brouillon, validé, facturé, annulé)",
        example="brouillon"
    )
    compagnie_id: UUID = Field(
        ...,
        description="Identifiant unique de la compagnie",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID
    utilisateur_id: UUID = Field(
        ...,
        description="Identifiant unique de l'utilisateur effectuant l'achat",
        example="123e4567-e89b-12d3-a456-426614174002"
    )  # UUID
    quantite_theorique: Optional[float] = Field(
        None,
        description="Quantité théorique pour les compensations",
        example=1000.0
    )
    quantite_reelle: Optional[float] = Field(
        None,
        description="Quantité réelle pour les compensations",
        example=950.0
    )
    created_at: datetime = Field(
        ...,
        description="Date de création de l'achat",
        example="2023-12-17T10:30:00.000000"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Date de dernière mise à jour",
        example="2023-12-17T10:30:00.000000"
    )

    class Config:
        from_attributes = True


class AchatCarburantSoldeResponse(AchatCarburantResponse):
    """Schéma pour la réponse d'un achat de carburant avec le solde."""
    montant_total_paiements: float = Field(
        0,
        description="Montant total des paiements effectués pour cet achat",
        example=2000000.0
    )
    solde_restant: float = Field(
        0,
        description="Solde restant à payer pour cet achat (montant_total - montant_total_paiements)",
        example=500000.0
    )


class LigneAchatCarburantResponse(BaseModel):
    """Schéma pour la réponse d'une ligne d'achat de carburant."""
    id: UUID = Field(
        ...,
        description="Identifiant unique de la ligne d'achat de carburant",
        example="123e4567-e89b-12d3-a456-426614174009"
    )  # UUID
    achat_carburant_id: UUID = Field(
        ...,
        description="Identifiant de l'achat de carburant auquel la ligne est associée",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    carburant_id: UUID = Field(
        ...,
        description="Identifiant du type de carburant",
        example="123e4567-e89b-12d3-a456-426614174004"
    )  # UUID
    quantite: float = Field(
        ...,
        description="Quantité de carburant",
        ge=0,
        example=1000.0
    )
    prix_unitaire: float = Field(
        ...,
        description="Prix unitaire du carburant",
        ge=0,
        example=1500.0
    )
    montant: float = Field(
        ...,
        description="Montant total pour cette ligne",
        ge=0,
        example=1500000.0
    )
    station_id: UUID = Field(
        ...,
        description="Identifiant unique de la station de destination",
        example="123e4567-e89b-12d3-a456-426614174001"
    )  # UUID
    created_at: datetime = Field(
        ...,
        description="Date de création de la ligne d'achat",
        example="2023-12-17T10:30:00.000000"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Date de dernière mise à jour",
        example="2023-12-17T10:30:00.000000"
    )

    class Config:
        from_attributes = True


class CompensationFinanciereResponse(BaseModel):
    """Schéma pour la réponse d'une compensation financière."""
    id: UUID = Field(
        ...,
        description="Identifiant unique de la compensation financière",
        example="123e4567-e89b-12d3-a456-426614174010"
    )  # UUID
    achat_carburant_id: UUID = Field(
        ...,
        description="Identifiant de l'achat de carburant concerné par la compensation",
        example="123e4567-e89b-12d3-a456-426614174003"
    )  # UUID
    type_compensation: str = Field(
        ...,
        description="Type de compensation ('avoir_reçu' ou 'avoir_dû')",
        example="avoir_reçu"
    )  # "avoir_reçu", "avoir_dû"
    quantite_theorique: float = Field(
        ...,
        description="Quantité théorique prévue dans l'achat",
        ge=0,
        example=1000.0
    )
    quantite_reelle: float = Field(
        ...,
        description="Quantité réellement livrée",
        ge=0,
        example=950.0
    )
    difference: float = Field(
        ...,
        description="Différence entre la quantité réelle et la quantité théorique",
        example=50.0
    )
    montant_compensation: float = Field(
        ...,
        description="Montant de la compensation",
        ge=0,
        example=75000.0
    )
    motif: Optional[str] = Field(
        None,
        description="Motif de la compensation",
        example="Perte en transit"
    )
    statut: str = Field(
        "émis",
        description="Statut de la compensation (émis, utilisé, partiellement_utilisé, expiré)",
        example="émis"
    )  # émis, utilisé, partiellement_utilisé, expiré
    created_at: datetime = Field(
        ...,
        description="Date de création de la compensation",
        example="2023-12-17T10:30:00.000000"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Date de dernière mise à jour",
        example="2023-12-17T10:30:00.000000"
    )

    class Config:
        from_attributes = True


class AvoirCompensationResponse(BaseModel):
    """Schéma pour la réponse d'un avoir de compensation."""
    id: UUID = Field(
        ...,
        description="Identifiant unique de l'avoir de compensation",
        example="123e4567-e89b-12d3-a456-426614174011"
    )  # UUID
    compensation_financiere_id: UUID = Field(
        ...,
        description="Identifiant de la compensation financière à laquelle l'avoir est lié",
        example="123e4567-e89b-12d3-a456-426614174006"
    )  # UUID
    tiers_id: UUID = Field(
        ...,
        description="Identifiant du tiers (fournisseur ou client) concerné",
        example="123e4567-e89b-12d3-a456-426614174007"
    )  # UUID
    montant: float = Field(
        ...,
        description="Montant de l'avoir",
        ge=0,
        example=75000.0
    )
    motif: str = Field(
        ...,
        description="Motif de l'avoir de compensation",
        example="Perte en transit"
    )
    date_emission: datetime = Field(
        ...,
        description="Date d'émission de l'avoir",
        example="2023-12-17T10:30:00.000000"
    )

    class Config:
        from_attributes = True

class PaiementAchatCarburantResponse(BaseModel):
    """Schéma pour la réponse d'un paiement d'achat de carburant."""
    id: UUID = Field(
        ...,
        description="Identifiant unique du paiement d'achat de carburant",
        example="123e4567-e89b-12d3-a456-426614174012"
    )
    achat_carburant_id: UUID = Field(
        ...,
        description="Identifiant de l'achat de carburant concerné par le paiement",
        example="123e4567-e89b-12d3-a456-426614174003"
    )
    date_paiement: datetime = Field(
        ...,
        description="Date du paiement au format ISO (AAAA-MM-JJTHH:MM:SS.mmmmmm)",
        example="2023-12-18T10:30:00.000000"
    )
    montant: float = Field(
        ...,
        description="Montant du paiement",
        ge=0,
        example=2500000.0
    )
    mode_paiement: str = Field(
        ...,
        description="Mode de paiement (espèces, chèque, virement, carte_bancaire, etc.)",
        example="virement"
    )
    tresorerie_station_id: UUID = Field(
        ...,
        description="Identifiant de la trésorerie station concernée par le paiement",
        example="123e4567-e89b-12d3-a456-426614174009"
    )
    statut: str = Field(
        "enregistré",
        description="Statut du paiement (enregistré, validé, annulé)",
        example="enregistré"
    )
    created_at: datetime = Field(
        ...,
        description="Date de création du paiement",
        example="2023-12-18T10:30:00.000000"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Date de dernière mise à jour",
        example="2023-12-18T10:30:00.000000"
    )

    class Config:
        from_attributes = True


class PaiementAchatCarburantSoldeResponse(PaiementAchatCarburantResponse):
    """Schéma pour la réponse d'un paiement d'achat de carburant avec le solde."""
    solde_restant_achat: float = Field(
        0,
        description="Solde restant à payer pour l'achat concerné par ce paiement",
        example=500000.0
    )