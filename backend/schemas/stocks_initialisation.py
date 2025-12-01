from pydantic import BaseModel
from typing import Optional
from datetime import date


# Schémas pour la qualité du carburant initial
class QualiteCarburantInitialBase(BaseModel):
    cuve_id: Optional[str] = None
    carburant_id: Optional[str] = None
    date_analyse: date
    utilisateur_id: Optional[str] = None
    densite: Optional[float] = None  # Ex: 0.8350 kg/L
    indice_octane: Optional[int] = None  # Ex: 95 pour SP95
    soufre_ppm: Optional[float] = None  # Partie par million
    type_additif: Optional[str] = None  # Type d'additif utilisé
    commentaire_qualite: Optional[str] = None
    resultat_qualite: Optional[str] = None  # 'Conforme', 'Non conforme', 'En attente'
    compagnie_id: Optional[str] = None


class QualiteCarburantInitialCreate(QualiteCarburantInitialBase):
    date_analyse: date


class QualiteCarburantInitialUpdate(BaseModel):
    densite: Optional[float] = None
    indice_octane: Optional[int] = None
    soufre_ppm: Optional[float] = None
    type_additif: Optional[str] = None
    commentaire_qualite: Optional[str] = None
    resultat_qualite: Optional[str] = None  # 'Conforme', 'Non conforme', 'En attente'


class QualiteCarburantInitialResponse(QualiteCarburantInitialBase):
    id: str
    created_at: str

    class Config:
        from_attributes = True


# Schémas pour les coûts logistiques initiaux
class CoutLogistiqueStockInitialBase(BaseModel):
    type_cout: str  # 'transport', 'stockage', 'manutention', 'assurance', 'autres'
    description: Optional[str] = None
    montant: float
    date_cout: date
    article_id: Optional[str] = None
    cuve_id: Optional[str] = None
    station_id: Optional[str] = None
    fournisseur_id: Optional[str] = None
    utilisateur_saisie_id: Optional[str] = None
    compagnie_id: Optional[str] = None


class CoutLogistiqueStockInitialCreate(CoutLogistiqueStockInitialBase):
    pass


class CoutLogistiqueStockInitialUpdate(BaseModel):
    type_cout: Optional[str] = None
    description: Optional[str] = None
    montant: Optional[float] = None
    date_cout: Optional[date] = None
    article_id: Optional[str] = None
    cuve_id: Optional[str] = None
    station_id: Optional[str] = None
    fournisseur_id: Optional[str] = None
    utilisateur_saisie_id: Optional[str] = None


class CoutLogistiqueStockInitialResponse(CoutLogistiqueStockInitialBase):
    id: str
    created_at: str

    class Config:
        from_attributes = True


# Schémas pour le bilan initial
class BilanInitialBase(BaseModel):
    compagnie_id: Optional[str] = None
    date_bilan: date
    commentaire: Optional[str] = None
    valeur_totale_stocks: Optional[float] = 0.0
    nombre_elements: Optional[int] = 0
    statut: Optional[str] = "Brouillon"  # 'Brouillon', 'En cours', 'Termine', 'Validé'


class BilanInitialCreate(BilanInitialBase):
    pass


class BilanInitialUpdate(BaseModel):
    commentaire: Optional[str] = None
    statut: Optional[str] = None  # 'Brouillon', 'En cours', 'Termine', 'Validé'
    utilisateur_validation_id: Optional[str] = None
    date_validation: Optional[date] = None


class BilanInitialSummary(BaseModel):
    id: str
    compagnie_id: str
    date_bilan: date
    valeur_totale_stocks: float
    nombre_elements: int
    statut: str
    est_valide: bool
    created_at: str

    class Config:
        from_attributes = True


class BilanInitialResponse(BilanInitialBase):
    id: str
    utilisateur_validation_id: Optional[str] = None
    date_validation: Optional[date] = None
    est_valide: bool
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# Schémas pour les lignes du bilan initial
class BilanInitialLigneBase(BaseModel):
    bilan_initial_stocks_id: str
    type_element: str  # 'carburant', 'article_boutique', 'autre'
    element_id: str  # ID de la cuve ou de l'article
    description_element: Optional[str] = None
    quantite: float
    unite_mesure: Optional[str] = None
    prix_unitaire: float
    valeur_totale: Optional[float] = None  # Générée à partir de quantité * prix_unitaire
    taux_tva: Optional[float] = 0.0
    montant_tva: Optional[float] = None
    montant_ht: Optional[float] = None


class BilanInitialLigneCreate(BilanInitialLigneBase):
    pass


class BilanInitialLigneUpdate(BaseModel):
    description_element: Optional[str] = None
    quantite: Optional[float] = None
    unite_mesure: Optional[str] = None
    prix_unitaire: Optional[float] = None
    taux_tva: Optional[float] = None


class BilanInitialLigneResponse(BilanInitialLigneBase):
    id: str
    created_at: str

    class Config:
        from_attributes = True