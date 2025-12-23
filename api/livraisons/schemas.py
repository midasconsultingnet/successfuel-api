from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LivraisonCreate(BaseModel):
    achat_carburant_id: Optional[str] = Field(
        None,
        description="Identifiant unique de l'achat de carburant d'origine",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    station_id: str = Field(
        ...,
        description="Identifiant unique de la station de livraison",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    cuve_id: str = Field(
        ...,
        description="Identifiant unique de la cuve qui reçoit la livraison de carburant",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    carburant_id: str = Field(
        ...,
        description="Identifiant unique du type de carburant livré",
        example="987fb8a6-c5b4-4a2d-bf6d-1e8f9a0c3b4d"
    )
    quantite_livree: float = Field(
        ...,
        ge=0,
        description="Quantité de carburant livrée en litres (décimal)",
        example=5000.0
    )
    quantite_commandee: Optional[float] = Field(
        None,
        ge=0,
        description="Quantité de carburant commandée en litres (décimal)",
        example=5000.0
    )
    date_livraison: datetime = Field(
        ...,
        description="Date et heure de la livraison",
        example="2023-10-15T09:30:00"
    )
    prix_unitaire: Optional[float] = Field(
        None,
        ge=0,
        description="Prix unitaire du carburant en devise locale par litre",
        example=1.25
    )
    jauge_avant_livraison: Optional[float] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve avant la livraison (en litres)",
        example=2000.0
    )
    jauge_apres_livraison: Optional[float] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve après la livraison (en litres)",
        example=7000.0
    )
    utilisateur_id: str = Field(
        ...,
        description="Identifiant unique de l'utilisateur qui a enregistré la livraison",
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef"
    )
    information: Optional[dict] = Field(
        None,
        description="Informations supplémentaires stockées au format JSON",
        example={"numero_bl": "BL-2023-10-001", "driver_name": "John Doe", "vehicle_plate": "AB-123-CD"}
    )
    numero_facture: Optional[str] = Field(
        None,
        max_length=50,
        description="Numéro de la facture associée à la livraison",
        example="FAC-2023-10-001"
    )
    compagnie_id: str = Field(
        ...,
        description="Identifiant unique de la compagnie associée à la livraison",
        example="123e4567-e89b-12d3-a456-426614174011"
    )
    statut_livraison: Optional[str] = Field(
        "en_attente",
        description="Statut de la livraison: en_attente, en_cours, livre_completement, livre_partiellement, en_retard",
        example="en_attente"
    )


class LivraisonResponse(BaseModel):
    id: str = Field(
        ...,
        description="Identifiant unique de la livraison",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    achat_carburant_id: Optional[str] = Field(
        None,
        description="Identifiant unique de l'achat de carburant d'origine",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    station_id: str = Field(
        ...,
        description="Identifiant de la station où la livraison a eu lieu",
        example="123e4567-e89b-12d3-a456-426614174010"
    )
    cuve_id: str = Field(
        ...,
        description="Identifiant unique de la cuve qui reçoit la livraison de carburant",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    carburant_id: str = Field(
        ...,
        description="Identifiant unique du type de carburant livré",
        example="987fb8a6-c5b4-4a2d-bf6d-1e8f9a0c3b4d"
    )
    quantite_livree: float = Field(
        ...,
        ge=0,
        description="Quantité de carburant livrée en litres (décimal)",
        example=5000.0
    )
    quantite_commandee: Optional[float] = Field(
        None,
        ge=0,
        description="Quantité de carburant commandée en litres (décimal)",
        example=5000.0
    )
    date_livraison: datetime = Field(
        ...,
        description="Date et heure de la livraison",
        example="2023-10-15T09:30:00"
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
        description="Montant total de la livraison",
        example=6250.00
    )
    jauge_avant_livraison: Optional[float] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve avant la livraison (en litres)",
        example=2000.0
    )
    jauge_apres_livraison: Optional[float] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve après la livraison (en litres)",
        example=7000.0
    )
    utilisateur_id: str = Field(
        ...,
        description="Identifiant unique de l'utilisateur qui a enregistré la livraison",
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef"
    )
    information: Optional[dict] = Field(
        None,
        description="Informations supplémentaires stockées au format JSON",
        example={"numero_bl": "BL-2023-10-001", "driver_name": "John Doe", "vehicle_plate": "AB-123-CD"}
    )
    numero_facture: Optional[str] = Field(
        None,
        max_length=50,
        description="Numéro de la facture associée à la livraison",
        example="FAC-2023-10-001"
    )
    compagnie_id: str = Field(
        ...,
        description="Identifiant de la compagnie associée à la livraison",
        example="123e4567-e89b-12d3-a456-426614174011"
    )
    statut_livraison: str = Field(
        ...,
        description="Statut de la livraison: en_attente, en_cours, livre_completement, livre_partiellement, en_retard",
        example="en_attente"
    )
    created_at: datetime = Field(
        ...,
        description="Date de création de la livraison",
        example="2023-10-15T09:30:00"
    )
    updated_at: datetime = Field(
        ...,
        description="Date de dernière mise à jour de la livraison",
        example="2023-10-15T09:30:00"
    )
    est_actif: bool = Field(
        True,
        description="Indique si la livraison est active ou supprimée"
    )

    class Config:
        from_attributes = True

class LivraisonUpdate(BaseModel):
    achat_carburant_id: Optional[str] = Field(
        None,
        description="Identifiant unique de l'achat de carburant d'origine",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    cuve_id: Optional[str] = Field(
        None,
        description="Identifiant unique de la cuve qui reçoit la livraison de carburant",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    carburant_id: Optional[str] = Field(
        None,
        description="Identifiant unique du type de carburant livré",
        example="987fb8a6-c5b4-4a2d-bf6d-1e8f9a0c3b4d"
    )
    quantite_livree: Optional[float] = Field(
        None,
        ge=0,
        description="Quantité de carburant livrée en litres (décimal)",
        example=5000.0
    )
    quantite_commandee: Optional[float] = Field(
        None,
        ge=0,
        description="Quantité de carburant commandée en litres (décimal)",
        example=5000.0
    )
    date_livraison: Optional[datetime] = Field(
        None,
        description="Date et heure de la livraison",
        example="2023-10-15T09:30:00"
    )
    prix_unitaire: Optional[float] = Field(
        None,
        ge=0,
        description="Prix unitaire du carburant en devise locale par litre",
        example=1.25
    )
    jauge_avant_livraison: Optional[float] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve avant la livraison (en litres)",
        example=2000.0
    )
    jauge_apres_livraison: Optional[float] = Field(
        None,
        ge=0,
        description="Niveau de jauge de la cuve après la livraison (en litres)",
        example=7000.0
    )
    information: Optional[dict] = Field(
        None,
        description="Informations supplémentaires stockées au format JSON",
        example={"numero_bl": "BL-2023-10-001", "driver_name": "John Doe", "vehicle_plate": "AB-123-CD"}
    )
    numero_facture: Optional[str] = Field(
        None,
        max_length=50,
        description="Numéro de la facture associée à la livraison",
        example="FAC-2023-10-001"
    )
    statut_livraison: Optional[str] = Field(
        None,
        description="Statut de la livraison: en_attente, en_cours, livre_completement, livre_partiellement, en_retard",
        example="en_attente"
    )