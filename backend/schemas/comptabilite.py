from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID
import json

# Plan Comptable Schemas
class PlanComptableBase(BaseModel):
    numero: str = Field(..., max_length=20, description="Numéro de compte comptable")
    intitule: str = Field(..., max_length=255, description="Nom du compte")
    classe: str = Field(..., max_length=5, description="Classe comptable")
    type_compte: str = Field(..., max_length=100, description="Type de compte")
    sens_solde: Optional[str] = Field(None, regex=r"^(D|C)$", description="Sens de solde (D pour débit, C pour crédit)")
    description: Optional[str] = None
    statut: str = Field(default="Actif", regex=r"^(Actif|Inactif|Supprime)$")
    est_compte_racine: bool = False
    est_compte_de_resultat: bool = False
    est_compte_actif: bool = True
    pays_id: Optional[UUID] = None
    est_specifique_pays: bool = False
    code_pays: Optional[str] = Field(None, max_length=3)
    compagnie_id: UUID

class PlanComptableCreate(PlanComptableBase):
    pass

class PlanComptableUpdate(BaseModel):
    intitule: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    statut: Optional[str] = Field(None, regex=r"^(Actif|Inactif|Supprime)$")
    compte_parent_id: Optional[UUID] = None

class PlanComptableResponse(PlanComptableBase):
    id: UUID
    compte_parent_id: Optional[UUID] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# Journal Schemas
class JournalBase(BaseModel):
    code: str = Field(..., max_length=20, description="Code du journal")
    libelle: str = Field(..., max_length=100, description="Libellé du journal")
    description: Optional[str] = None
    type_journal: str = Field(..., regex=r"^(achats|ventes|tresorerie|banque|caisse|opex|stock|autre)$", description="Type d'opérations")
    pays_id: Optional[UUID] = None
    compagnie_id: UUID
    statut: str = Field(default="Actif", regex=r"^(Actif|Inactif|Supprime)$")

class JournalCreate(JournalBase):
    pass

class JournalResponse(JournalBase):
    id: UUID
    derniere_piece: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# Écriture Comptable Schemas
class LigneEcritureBase(BaseModel):
    compte_id: UUID
    montant_debit: float = 0.0
    montant_credit: float = 0.0
    libelle: Optional[str] = None
    tiers_id: Optional[UUID] = None
    projet_id: Optional[UUID] = None

class LigneEcritureCreate(LigneEcritureBase):
    pass

class LigneEcritureResponse(LigneEcritureBase):
    id: UUID
    created_at: str

    class Config:
        from_attributes = True

class EcritureComptableBase(BaseModel):
    journal_id: UUID
    date_ecriture: date
    libelle: str
    tiers_id: Optional[UUID] = None
    operation_id: Optional[UUID] = None
    operation_type: Optional[str] = None
    reference_externe: Optional[str] = None
    compagnie_id: UUID

class EcritureComptableCreate(EcritureComptableBase):
    lignes: List[LigneEcritureCreate]

class EcritureComptableUpdate(BaseModel):
    libelle: Optional[str] = None
    tiers_id: Optional[UUID] = None
    operation_id: Optional[UUID] = None
    operation_type: Optional[str] = None
    est_validee: Optional[bool] = None
    reference_externe: Optional[str] = None

class EcritureComptableResponse(EcritureComptableBase):
    id: UUID
    numero_piece: str
    montant_debit: float
    montant_credit: float
    est_validee: bool
    est_cloturee: bool
    date_validation: Optional[str] = None
    utilisateur_id: Optional[UUID] = None
    utilisateur_validation_id: Optional[UUID] = None
    created_at: str
    updated_at: str
    lignes: List[LigneEcritureResponse] = []

    class Config:
        from_attributes = True

# Solde Compte Schemas
class SoldeCompteBase(BaseModel):
    compte_id: UUID
    date_solde: date
    solde_debit: float
    solde_credit: float
    type_solde: str = Field(..., regex=r"^(ouverture|cloture|intermediaire)$")
    compagnie_id: UUID

class SoldeCompteCreate(SoldeCompteBase):
    pass

class SoldeCompteResponse(SoldeCompteBase):
    id: UUID
    created_at: str
    solde_net: float

    class Config:
        from_attributes = True

# Bilan Initial Schemas
class BilanInitialLigneBase(BaseModel):
    compte_numero: str = Field(..., max_length=20)
    montant_initial: float
    type_solde: str = Field(..., regex=r"^(debit|credit)$")
    poste_bilan: str = Field(..., regex=r"^(actif|passif|capitaux_propres)$")
    categorie_detaillee: Optional[str] = Field(None, max_length=50)
    commentaire: Optional[str] = None

class BilanInitialLigneCreate(BilanInitialLigneBase):
    compte_id: Optional[UUID] = None

class BilanInitialLigneResponse(BilanInitialLigneBase):
    id: UUID
    compte_id: Optional[UUID] = None
    created_at: str

    class Config:
        from_attributes = True

class ImmobilisationBilanInitialBase(BaseModel):
    code: str = Field(..., max_length=50)
    libelle: str
    categorie: str = Field(..., max_length=100)
    date_achat: date
    valeur_acquisition: float
    valeur_nette_comptable: float
    amortissement_cumule: float
    duree_amortissement: Optional[int] = 0
    date_fin_amortissement: Optional[date] = None
    fournisseur_id: Optional[UUID] = None
    utilisateur_achat_id: Optional[UUID] = None
    observation: Optional[str] = None
    statut: str = Field(default="Actif", regex=r"^(Actif|Cede|Hors service|Vendu)$")

class ImmobilisationBilanInitialCreate(ImmobilisationBilanInitialBase):
    pass

class ImmobilisationBilanInitialResponse(ImmobilisationBilanInitialBase):
    id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class StockBilanInitialBase(BaseModel):
    type_stock: str = Field(..., regex=r"^(carburant|produit_boutique)$")
    quantite: float
    prix_unitaire: float
    commentaire: Optional[str] = None

class StockBilanInitialCreate(StockBilanInitialBase):
    article_id: Optional[UUID] = None
    carburant_id: Optional[UUID] = None
    cuve_id: Optional[UUID] = None

class StockBilanInitialResponse(StockBilanInitialBase):
    id: UUID
    article_id: Optional[UUID] = None
    carburant_id: Optional[UUID] = None
    cuve_id: Optional[UUID] = None
    valeur_totale: float
    created_at: str

    class Config:
        from_attributes = True

class CreanceDetteBilanInitialBase(BaseModel):
    type_tiers: str = Field(..., regex=r"^(client|fournisseur)$")
    tiers_id: UUID
    montant_initial: float
    devise: str = "MGA"
    date_echeance: Optional[date] = None
    reference_piece: Optional[str] = Field(None, max_length=100)
    commentaire: Optional[str] = None

class CreanceDetteBilanInitialCreate(CreanceDetteBilanInitialBase):
    pass

class CreanceDetteBilanInitialResponse(CreanceDetteBilanInitialBase):
    id: UUID
    created_at: str

    class Config:
        from_attributes = True

class BilanInitialBase(BaseModel):
    compagnie_id: UUID
    date_bilan_initial: date
    commentaire: Optional[str] = None
    utilisateur_id: Optional[UUID] = None
    description: Optional[str] = None

class BilanInitialCreate(BilanInitialBase):
    lignes: List[BilanInitialLigneCreate] = []
    immobilisations: List[ImmobilisationBilanInitialCreate] = []
    stocks: List[StockBilanInitialCreate] = []
    creances_dettes: List[CreanceDetteBilanInitialCreate] = []

class BilanInitialUpdate(BaseModel):
    commentaire: Optional[str] = None
    est_valide: Optional[bool] = None
    est_verifie: Optional[bool] = None

class BilanInitialResponse(BilanInitialBase):
    id: UUID
    est_valide: bool
    est_verifie: bool
    created_at: str
    updated_at: str
    lignes: List[BilanInitialLigneResponse] = []
    immobilisations: List[ImmobilisationBilanInitialResponse] = []
    stocks: List[StockBilanInitialResponse] = []
    creances_dettes: List[CreanceDetteBilanInitialResponse] = []

    class Config:
        from_attributes = True

# Rapport Schemas
class RapportFinancierBase(BaseModel):
    type_rapport: str = Field(..., regex=r"^(bilan|compte_resultat|grand_livre|balance|journal|tva|etat_tva)$")
    periode_debut: date
    periode_fin: date
    format_sortie: str = "PDF"
    utilisateur_generateur_id: Optional[UUID] = None
    compagnie_id: UUID
    station_id: Optional[UUID] = None
    commentaire: Optional[str] = None

class RapportFinancierCreate(RapportFinancierBase):
    pass

class RapportFinancierUpdate(BaseModel):
    commentaire: Optional[str] = None
    statut: Optional[str] = Field(None, regex=r"^(En cours|Termine|Erreur|Archive)$")

class RapportFinancierResponse(RapportFinancierBase):
    id: UUID
    contenu: Optional[str] = None  # JSON as string
    statut: str = "En cours"
    fichier_joint: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class HistoriqueRapportBase(BaseModel):
    nom_rapport: str = Field(..., max_length=100)
    type_rapport: str
    periode_debut: date
    periode_fin: date
    utilisateur_demandeur_id: Optional[UUID] = None
    compagnie_id: UUID
    station_id: Optional[UUID] = None

class HistoriqueRapportCreate(HistoriqueRapportBase):
    pass

class HistoriqueRapportResponse(HistoriqueRapportBase):
    id: UUID
    statut: str
    parametres: Optional[str] = None  # JSON as string
    resultat_generation: Optional[str] = None
    date_demande: str
    date_generation: Optional[str] = None
    date_consultation: Optional[str] = None
    est_a_jour: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True