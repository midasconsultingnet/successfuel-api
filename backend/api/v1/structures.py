import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from database.database import get_db
from models.structures import Pays, Compagnie, Station, Utilisateur, Carburant, Client, Fournisseur, Employe, TypeTiers
from services.structures_service import (
    create_pays, get_pays_by_id, get_pays_by_code, get_all_pays, update_pays,
    create_compagnie, get_compagnie_by_id, get_compagnie_by_code, get_all_compagnies, update_compagnie,
    create_station, get_station_by_id, get_station_by_code, get_all_stations, update_station,
    create_barremage_cuves, get_barremage_cuves_by_id, get_all_barremage_cuves, update_barremage_cuves, delete_barremage_cuves,
    create_pompe, get_pompe_by_id, get_all_pompes, update_pompe, delete_pompe,
    create_pistolet, get_pistolet_by_id, get_all_pistolets, update_pistolet, delete_pistolet,
    create_historique_prix_carburant, get_historique_prix_carburant_by_id, get_all_historique_prix_carburant,
    create_historique_prix_article, get_historique_prix_article_by_id, get_all_historique_prix_article,
    create_historique_index_pistolet, get_historique_index_pistolet_by_id, get_all_historique_index_pistolet,
    create_cuve, get_cuve_by_id, get_all_cuves, update_cuve, delete_cuve,
    create_carburant, get_carburant_by_id, get_carburant_by_code, get_all_carburants, update_carburant, delete_carburant,
    create_article, get_article_by_code, get_article_by_id, get_all_articles,
    create_client, get_client_by_code, get_client_by_id, get_all_clients,
    create_fournisseur, get_fournisseur_by_code, get_fournisseur_by_id, get_all_fournisseurs,
    create_employe, get_employe_by_code, get_employe_by_id, get_all_employes,
    create_type_tiers, get_type_tiers_by_id, get_all_types_tiers, get_type_tiers_by_type
)
from services.auth_service import get_user_by_id
from utils.security import verify_token
from utils.dependencies import get_current_user
from utils.access_control import require_permission, prohibit_super_admin_access, create_permission_dependency

# Configuration du logging pour debugger les imports
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Chargement du module structures.py")
from pydantic import BaseModel
from services.excel_import_service import import_barremage_from_excel


# Create API router
router = APIRouter(
    tags=["structures"],
    responses={404: {"description": "Endpoint non trouvé"}}
)

logger.info("Routeur créé avec succès")


# Request/response models
class PaysBase(BaseModel):
    code_pays: str
    nom_pays: str
    devise_principale: str = "MGA"
    taux_tva_par_defaut: float = 20.00
    systeme_comptable: str = "IFRS"
    date_application_tva: Optional[str] = None
    statut: str = "Actif"


class PaysCreate(PaysBase):
    pass


class PaysUpdate(BaseModel):
    nom_pays: Optional[str] = None
    devise_principale: Optional[str] = None
    taux_tva_par_defaut: Optional[float] = None
    systeme_comptable: Optional[str] = None
    date_application_tva: Optional[str] = None
    statut: Optional[str] = None


class PaysResponse(BaseModel):
    id: str
    code_pays: str
    nom_pays: str
    devise_principale: str
    taux_tva_par_defaut: float
    systeme_comptable: str
    date_application_tva: Optional[str] = None
    statut: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class CompagnieBase(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    pays_id: Optional[str] = None
    devise_principale: str = "MGA"


class CompagnieCreate(CompagnieBase):
    pass


class CompagnieUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    pays_id: Optional[str] = None
    devise_principale: Optional[str] = None
    statut: Optional[str] = None


class CompagnieResponse(BaseModel):
    id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    statut: str
    pays_id: Optional[str] = None
    devise_principale: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class StationBase(BaseModel):
    compagnie_id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pays_id: Optional[str] = None


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    compagnie_id: Optional[str] = None
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pays_id: Optional[str] = None
    statut: Optional[str] = None


class StationResponse(BaseModel):
    id: str
    compagnie_id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pays_id: Optional[str] = None
    statut: str
    created_at: str

    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    total: int
    limit: int
    offset: int


class PaysListResponse(BaseModel):
    success: bool
    data: List[PaysResponse]
    pagination: PaginationResponse


class CompagnieListResponse(BaseModel):
    success: bool
    data: List[CompagnieResponse]
    pagination: PaginationResponse


class StationListResponse(BaseModel):
    success: bool
    data: List[StationResponse]
    pagination: PaginationResponse


class StationCreateNonAdmin(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None


class BarremageCuveBase(BaseModel):
    cuve_id: str
    station_id: str
    hauteur: float
    volume: float
    statut: str = "Actif"


class BarremageCuveCreate(BarremageCuveBase):
    pass


class BarremageCuveUpdate(BaseModel):
    hauteur: Optional[float] = None
    volume: Optional[float] = None
    statut: Optional[str] = None


class BarremageCuveResponse(BaseModel):
    id: str
    cuve_id: str
    station_id: str
    hauteur: float
    volume: float
    statut: str
    compagnie_id: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class BarremageCuveListResponse(BaseModel):
    success: bool
    data: List[BarremageCuveResponse]
    pagination: PaginationResponse


class CuveBase(BaseModel):
    station_id: str
    code: str
    capacite: float
    carburant_id: Optional[str] = None
    temperature: float = 0.0
    statut: str = "Actif"


class CuveCreate(CuveBase):
    pass


class CuveUpdate(BaseModel):
    station_id: Optional[str] = None
    code: Optional[str] = None
    capacite: Optional[float] = None
    carburant_id: Optional[str] = None
    temperature: Optional[float] = None
    statut: Optional[str] = None


class CuveResponse(BaseModel):
    id: str
    station_id: str
    code: str
    capacite: float
    carburant_id: Optional[str] = None
    compagnie_id: str
    temperature: float
    statut: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class CuveListResponse(BaseModel):
    success: bool
    data: List[CuveResponse]
    pagination: PaginationResponse


class CarburantBase(BaseModel):
    code: str
    libelle: str
    type: str  # Ex: "Essence", "Gasoil", "Pétrole"
    compagnie_id: str
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    statut: str = "Actif"


class CarburantCreate(CarburantBase):
    pass


class CarburantCreateNonAdmin(BaseModel):
    code: str
    libelle: str
    type: str  # Ex: "Essence", "Gasoil", "Pétrole"
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    statut: str = "Actif"


class CarburantUpdate(BaseModel):
    libelle: Optional[str] = None
    type: Optional[str] = None
    prix_achat: Optional[float] = None
    prix_vente: Optional[float] = None
    statut: Optional[str] = None


class CarburantResponse(BaseModel):
    id: str
    code: str
    libelle: str
    type: str
    compagnie_id: str
    prix_achat: float
    prix_vente: float
    qualite: Optional[float] = 1.00  # Note de qualité sur 10
    statut: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class CarburantListResponse(BaseModel):
    success: bool
    data: List[CarburantResponse]
    pagination: PaginationResponse


class PompeBase(BaseModel):
    station_id: str
    code: str
    statut: str = "Actif"


class PompeCreate(PompeBase):
    pass


class PompeUpdate(BaseModel):
    station_id: Optional[str] = None
    code: Optional[str] = None
    statut: Optional[str] = None


class PompeResponse(BaseModel):
    id: str
    station_id: str
    code: str
    compagnie_id: str
    statut: str
    created_at: str

    class Config:
        from_attributes = True


class PompeListResponse(BaseModel):
    success: bool
    data: List[PompeResponse]
    pagination: PaginationResponse


class PistoletBase(BaseModel):
    code: str
    pompe_id: str
    cuve_id: str
    index_initiale: float = 0.0
    statut: str = "Actif"


class PistoletCreate(PistoletBase):
    pass


class PistoletCreateNonAdmin(BaseModel):
    code: str
    pompe_id: Optional[str] = None  # Rendu optionnel pour les non-admins
    cuve_id: str
    index_initiale: float = 0.0
    statut: str = "Actif"


class PistoletUpdate(BaseModel):
    code: Optional[str] = None
    pompe_id: Optional[str] = None
    cuve_id: Optional[str] = None
    index_initiale: Optional[float] = None
    statut: Optional[str] = None


class PistoletResponse(BaseModel):
    id: str
    code: str
    pompe_id: Optional[str] = None
    cuve_id: str
    index_initiale: float
    compagnie_id: str
    statut: str
    created_at: str

    class Config:
        from_attributes = True


class PistoletListResponse(BaseModel):
    success: bool
    data: List[PistoletResponse]
    pagination: PaginationResponse


class HistoriquePrixCarburantBase(BaseModel):
    carburant_id: str
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    date_application: str  # format: YYYY-MM-DD
    utilisateur_id: Optional[str] = None


class HistoriquePrixCarburantCreate(HistoriquePrixCarburantBase):
    pass


class HistoriquePrixCarburantResponse(BaseModel):
    id: str
    carburant_id: str
    prix_achat: float
    prix_vente: float
    date_application: str
    utilisateur_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class HistoriquePrixCarburantListResponse(BaseModel):
    success: bool
    data: List[HistoriquePrixCarburantResponse]
    pagination: PaginationResponse


class ArticleBase(BaseModel):
    code: str
    libelle: str
    codebarre: Optional[str] = None
    famille_id: Optional[str] = None
    unite: str = "Litre"
    compagnie_id: str
    type_article: str = "produit"  # CHECK (type_article IN ('produit', 'service'))
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    tva: float = 0.0
    stock_minimal: float = 0.0
    statut: str = "Actif"


class ArticleCreate(ArticleBase):
    pass


class ArticleCreateNonAdmin(BaseModel):
    code: str
    libelle: str
    codebarre: Optional[str] = None
    famille_id: Optional[str] = None
    unite: str = "Litre"
    type_article: str = "produit"  # CHECK (type_article IN ('produit', 'service'))
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    tva: float = 0.0
    stock_minimal: float = 0.0
    statut: str = "Actif"


class ArticleUpdate(BaseModel):
    libelle: Optional[str] = None
    codebarre: Optional[str] = None
    famille_id: Optional[str] = None
    unite: Optional[str] = None
    type_article: Optional[str] = None
    prix_achat: Optional[float] = None
    prix_vente: Optional[float] = None
    tva: Optional[float] = None
    stock_minimal: Optional[float] = None
    statut: Optional[str] = None


class ArticleResponse(BaseModel):
    id: str
    code: str
    libelle: str
    codebarre: Optional[str] = None
    famille_id: Optional[str] = None
    unite: str
    compagnie_id: str
    type_article: str  # CHECK (type_article IN ('produit', 'service'))
    prix_achat: float
    prix_vente: float
    tva: Optional[float] = 0.0
    stock_minimal: Optional[float] = 0.0
    statut: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    success: bool
    data: List[ArticleResponse]
    pagination: PaginationResponse


class HistoriquePrixArticleBase(BaseModel):
    article_id: str
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    date_application: str  # format: YYYY-MM-DD
    utilisateur_id: Optional[str] = None


class HistoriquePrixArticleCreate(HistoriquePrixArticleBase):
    pass


class HistoriquePrixArticleResponse(BaseModel):
    id: str
    article_id: str
    prix_achat: float
    prix_vente: float
    date_application: str
    utilisateur_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class HistoriquePrixArticleListResponse(BaseModel):
    success: bool
    data: List[HistoriquePrixArticleResponse]
    pagination: PaginationResponse


class HistoriqueIndexPistoletBase(BaseModel):
    pistolet_id: str
    index_releve: float
    date_releve: str  # format: YYYY-MM-DD
    utilisateur_id: Optional[str] = None
    observation: Optional[str] = None


class HistoriqueIndexPistoletCreate(HistoriqueIndexPistoletBase):
    pass


class HistoriqueIndexPistoletResponse(BaseModel):
    id: str
    pistolet_id: str
    index_releve: float
    date_releve: str
    utilisateur_id: Optional[str] = None
    observation: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class HistoriqueIndexPistoletListResponse(BaseModel):
    success: bool
    data: List[HistoriqueIndexPistoletResponse]
    pagination: PaginationResponse


# Modèles pour les clients
class ClientBase(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    compagnie_id: str
    station_ids: Optional[list] = []
    type_tiers_id: Optional[str] = None
    statut: str = "Actif"
    nb_jrs_creance: int = 0
    devise_facturation: str = "MGA"


class ClientCreate(ClientBase):
    pass


class ClientCreateNonAdmin(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    station_ids: Optional[list] = []
    type_tiers_id: Optional[str] = None
    statut: str = "Actif"
    nb_jrs_creance: int = 0
    devise_facturation: str = "MGA"


class ClientUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    station_ids: Optional[list] = None
    type_tiers_id: Optional[str] = None
    statut: Optional[str] = None
    nb_jrs_creance: Optional[int] = None
    devise_facturation: Optional[str] = None


class ClientResponse(BaseModel):
    id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    compagnie_id: str
    station_ids: Optional[list] = []
    type_tiers_id: Optional[str] = None
    statut: str
    nb_jrs_creance: int
    solde_comptable: float
    solde_confirme: float
    date_dernier_rapprochement: Optional[str] = None
    devise_facturation: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    success: bool
    data: List[ClientResponse]
    pagination: PaginationResponse


# Modèles pour les fournisseurs
class FournisseurBase(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    compagnie_id: str
    station_ids: Optional[list] = []
    type_tiers_id: Optional[str] = None
    statut: str = "Actif"
    nb_jrs_creance: int = 0


class FournisseurCreate(FournisseurBase):
    pass


class FournisseurCreateNonAdmin(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    station_ids: Optional[list] = []
    type_tiers_id: Optional[str] = None
    statut: str = "Actif"
    nb_jrs_creance: int = 0


class FournisseurUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    station_ids: Optional[list] = None
    type_tiers_id: Optional[str] = None
    statut: Optional[str] = None
    nb_jrs_creance: Optional[int] = None


class FournisseurResponse(BaseModel):
    id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    compagnie_id: str
    station_ids: Optional[list] = []
    type_tiers_id: Optional[str] = None
    statut: str
    nb_jrs_creance: int
    solde_comptable: float
    solde_confirme: float
    date_dernier_rapprochement: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class FournisseurListResponse(BaseModel):
    success: bool
    data: List[FournisseurResponse]
    pagination: PaginationResponse


# Modèles pour les employés
class EmployeBase(BaseModel):
    code: str
    nom: str
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    poste: Optional[str] = None
    salaire_base: float = 0.0
    avances: float = 0.0
    creances: float = 0.0
    compagnie_id: str
    station_ids: Optional[list] = []
    statut: str = "Actif"


class EmployeCreate(EmployeBase):
    pass


class EmployeCreateNonAdmin(BaseModel):
    code: str
    nom: str
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    poste: Optional[str] = None
    salaire_base: float = 0.0
    avances: float = 0.0
    creances: float = 0.0
    station_ids: Optional[list] = []
    statut: str = "Actif"


class EmployeUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    poste: Optional[str] = None
    salaire_base: Optional[float] = None
    avances: Optional[float] = None
    creances: Optional[float] = None
    station_ids: Optional[list] = None
    statut: Optional[str] = None


class EmployeResponse(BaseModel):
    id: str
    code: str
    nom: str
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    poste: Optional[str] = None
    salaire_base: float
    avances: float
    creances: float
    compagnie_id: str
    station_ids: Optional[list] = []
    statut: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeListResponse(BaseModel):
    success: bool
    data: List[EmployeResponse]
    pagination: PaginationResponse


# Modèles pour les types de tiers
class TypeTiersBase(BaseModel):
    type: str
    libelle: str
    num_compte: Optional[str] = None


class TypeTiersCreate(TypeTiersBase):
    pass


class TypeTiersUpdate(BaseModel):
    libelle: Optional[str] = None
    num_compte: Optional[str] = None


class TypeTiersResponse(BaseModel):
    id: str
    type: str
    libelle: str
    num_compte: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class TypeTiersListResponse(BaseModel):
    success: bool
    data: List[TypeTiersResponse]
    pagination: PaginationResponse


@router.post("/pays", response_model=PaysResponse)
async def create_pays_endpoint(
    pays_data: PaysCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("pays.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new country
    Only accessible to super_administrateurs and administrateurs
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to create pays is restricted to admin users"
        )

    try:
        db_pays = create_pays(
            db,
            code_pays=pays_data.code_pays,
            nom_pays=pays_data.nom_pays,
            devise_principale=pays_data.devise_principale,
            taux_tva_par_defaut=pays_data.taux_tva_par_defaut,
            systeme_comptable=pays_data.systeme_comptable,
            date_application_tva=pays_data.date_application_tva,
            statut=pays_data.statut
        )

        return PaysResponse(
            id=str(db_pays.id),
            code_pays=db_pays.code_pays,
            nom_pays=db_pays.nom_pays,
            devise_principale=db_pays.devise_principale,
            taux_tva_par_defaut=float(db_pays.taux_tva_par_defaut),
            systeme_comptable=db_pays.systeme_comptable,
            date_application_tva=db_pays.date_application_tva.isoformat() if db_pays.date_application_tva else None,
            statut=db_pays.statut,
            created_at=db_pays.created_at.isoformat(),
            updated_at=db_pays.updated_at.isoformat() if db_pays.updated_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/pays", response_model=PaysListResponse)
async def get_pays_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in country name"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("pays.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all countries with optional filters
    """
    # Only admin users can access countries (countries are not company-specific)
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to countries information is restricted to admin users"
        )

    pays_list = get_all_pays(db, statut=statut, search=search)
    total = len(pays_list)

    # Apply pagination to the results
    paginated_pays = pays_list[offset:offset+limit]

    return PaysListResponse(
        success=True,
        data=[
            PaysResponse(
                id=str(pays.id),
                code_pays=pays.code_pays,
                nom_pays=pays.nom_pays,
                devise_principale=pays.devise_principale,
                taux_tva_par_defaut=float(pays.taux_tva_par_defaut),
                systeme_comptable=pays.systeme_comptable,
                date_application_tva=pays.date_application_tva.isoformat() if pays.date_application_tva else None,
                statut=pays.statut,
                created_at=pays.created_at.isoformat(),
                updated_at=pays.updated_at.isoformat() if pays.updated_at else None
            )
            for pays in paginated_pays
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.put("/pays/{pays_id}", response_model=PaysResponse)
async def update_pays_endpoint(
    pays_id: str,
    pays_data: PaysUpdate,
    current_user: Utilisateur = Depends(create_permission_dependency("pays.modifier")),
    db: Session = Depends(get_db)
):
    """
    Update a country
    """
    from datetime import datetime

    # Prepare data with proper date conversion
    update_data = pays_data.dict(exclude_unset=True)

    # Convert date_application_tva to proper date format if provided and not None
    if 'date_application_tva' in update_data:
        if update_data['date_application_tva'] is not None:
            try:
                # Try to parse the date string to ensure it's in a valid format
                if isinstance(update_data['date_application_tva'], str):
                    # Parse ISO format date (YYYY-MM-DD)
                    update_data['date_application_tva'] = datetime.strptime(update_data['date_application_tva'], "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format for date_application_tva. Expected format: YYYY-MM-DD"
                )
        # If the value is None, it's already handled correctly by SQLAlchemy

    updated_pays = update_pays(db, pays_id, **update_data)
    if not updated_pays:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )

    return PaysResponse(
        id=str(updated_pays.id),
        code_pays=updated_pays.code_pays,
        nom_pays=updated_pays.nom_pays,
        devise_principale=updated_pays.devise_principale,
        taux_tva_par_defaut=float(updated_pays.taux_tva_par_defaut),
        systeme_comptable=updated_pays.systeme_comptable,
        date_application_tva=updated_pays.date_application_tva.isoformat() if updated_pays.date_application_tva else None,
        statut=updated_pays.statut,
        created_at=updated_pays.created_at.isoformat(),
        updated_at=updated_pays.updated_at.isoformat() if updated_pays.updated_at else None
    )


@router.post("/companies", response_model=CompagnieResponse)
async def create_compagnie_endpoint(
    compagnie_data: CompagnieCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("compagnies.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new company
    Only accessible to super_administrateurs and administrateurs
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to create compagnies is restricted to admin users"
        )

    try:
        db_compagnie = create_compagnie(
            db,
            code=compagnie_data.code,
            nom=compagnie_data.nom,
            adresse=compagnie_data.adresse,
            telephone=compagnie_data.telephone,
            email=compagnie_data.email,
            nif=compagnie_data.nif,
            pays_id=compagnie_data.pays_id,
            devise_principale=compagnie_data.devise_principale
        )

        return CompagnieResponse(
            id=str(db_compagnie.id),
            code=db_compagnie.code,
            nom=db_compagnie.nom,
            adresse=db_compagnie.adresse,
            telephone=db_compagnie.telephone,
            email=db_compagnie.email,
            nif=db_compagnie.nif,
            statut=db_compagnie.statut,
            pays_id=str(db_compagnie.pays_id) if db_compagnie.pays_id else None,
            devise_principale=db_compagnie.devise_principale,
            created_at=db_compagnie.created_at.isoformat(),
            updated_at=db_compagnie.updated_at.isoformat() if db_compagnie.updated_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/companies", response_model=CompagnieListResponse)
async def get_compagnies_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    pays_id: Optional[str] = Query(None, description="Filter by country ID"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("compagnies.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all companies with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Only admin users can see all companies
    if is_admin_or_super_admin(user_type):
        # Admins can see all companies with optional filters
        compagnies_list = get_all_compagnies(db, statut=statut, pays_id=pays_id)
    else:
        # Non-admin users can only see their own company
        if current_user.compagnie_id:
            # Fetch only the user's company
            company = get_compagnie_by_id(db, str(current_user.compagnie_id))
            compagnies_list = [company] if company else []
        else:
            compagnies_list = []

    total = len(compagnies_list)

    # Apply pagination to the results
    paginated_compagnies = compagnies_list[offset:offset+limit]

    return CompagnieListResponse(
        success=True,
        data=[
            CompagnieResponse(
                id=str(compagnie.id),
                code=compagnie.code,
                nom=compagnie.nom,
                adresse=compagnie.adresse,
                telephone=compagnie.telephone,
                email=compagnie.email,
                nif=compagnie.nif,
                statut=compagnie.statut,
                pays_id=str(compagnie.pays_id) if compagnie.pays_id else None,
                devise_principale=compagnie.devise_principale,
                created_at=compagnie.created_at.isoformat(),
                updated_at=compagnie.updated_at.isoformat() if compagnie.updated_at else None
            )
            for compagnie in paginated_compagnies
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.get("/my-company", response_model=CompagnieResponse)
async def get_my_company(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the company details of the currently logged-in user
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint accessible only for non-admin users"
        )

    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not associated with user"
        )

    company = get_compagnie_by_id(db, str(current_user.compagnie_id))
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return CompagnieResponse(
        id=str(company.id),
        code=company.code,
        nom=company.nom,
        adresse=company.adresse,
        telephone=company.telephone,
        email=company.email,
        nif=company.nif,
        statut=company.statut,
        pays_id=str(company.pays_id) if company.pays_id else None,
        devise_principale=company.devise_principale,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat() if company.updated_at else None
    )


@router.put("/my-company", response_model=CompagnieResponse)
async def update_my_company(
    compagnie_data: CompagnieUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the company details of the currently logged-in user
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    user_type = current_user.type_utilisateur

    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint accessible only for non-admin users"
        )

    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not associated with user"
        )

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "compagnies.modifier"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'compagnies.modifier' required"
        )

    # Verify that the user belongs to the company they're trying to update
    user_compagnie_id = str(current_user.compagnie_id)
    updated_compagnie = update_compagnie(db, user_compagnie_id, **compagnie_data.dict(exclude_unset=True))
    if not updated_compagnie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return CompagnieResponse(
        id=str(updated_compagnie.id),
        code=updated_compagnie.code,
        nom=updated_compagnie.nom,
        adresse=updated_compagnie.adresse,
        telephone=updated_compagnie.telephone,
        email=updated_compagnie.email,
        nif=updated_compagnie.nif,
        statut=updated_compagnie.statut,
        pays_id=str(updated_compagnie.pays_id) if updated_compagnie.pays_id else None,
        devise_principale=updated_compagnie.devise_principale,
        created_at=updated_compagnie.created_at.isoformat(),
        updated_at=updated_compagnie.updated_at.isoformat() if updated_compagnie.updated_at else None
    )


@router.put("/companies/{compagnie_id}", response_model=CompagnieResponse)
async def update_compagnie_endpoint(
    compagnie_id: str,
    compagnie_data: CompagnieUpdate,
    current_user: Utilisateur = Depends(create_permission_dependency("compagnies.modifier")),
    db: Session = Depends(get_db)
):
    """
    Update a company
    """
    updated_compagnie = update_compagnie(db, compagnie_id, **compagnie_data.dict(exclude_unset=True))
    if not updated_compagnie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return CompagnieResponse(
        id=str(updated_compagnie.id),
        code=updated_compagnie.code,
        nom=updated_compagnie.nom,
        adresse=updated_compagnie.adresse,
        telephone=updated_compagnie.telephone,
        email=updated_compagnie.email,
        nif=updated_compagnie.nif,
        statut=updated_compagnie.statut,
        pays_id=str(updated_compagnie.pays_id) if updated_compagnie.pays_id else None,
        devise_principale=updated_compagnie.devise_principale,
        created_at=updated_compagnie.created_at.isoformat(),
        updated_at=updated_compagnie.updated_at.isoformat() if updated_compagnie.updated_at else None
    )


@router.post("/stations", response_model=StationResponse)
async def create_station_endpoint(
    station_data: StationCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("creer_stations")),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle station (réservé aux utilisateurs 'administrateur' et 'super_administrateur')
    Seul ce endpoint permet de spécifier explicitement le 'compagnie_id' et 'pays_id'
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Verify that only admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to admin users"
        )

    # For admin users, verify they have the required permission for the specified company
    if station_data.compagnie_id:
        # Verify that the user can access the specified company
        # Additional logic could be implemented here based on the user's permissions
        pass

    try:
        db_station = create_station(
            db,
            compagnie_id=station_data.compagnie_id,
            code=station_data.code,
            nom=station_data.nom,
            adresse=station_data.adresse,
            telephone=station_data.telephone,
            email=station_data.email,
            pays_id=station_data.pays_id
        )

        return StationResponse(
            id=str(db_station.id),
            compagnie_id=str(db_station.compagnie_id),
            code=db_station.code,
            nom=db_station.nom,
            adresse=db_station.adresse,
            telephone=db_station.telephone,
            email=db_station.email,
            pays_id=str(db_station.pays_id) if db_station.pays_id else None,
            statut=db_station.statut,
            created_at=db_station.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/my-stations", response_model=StationResponse)
async def create_my_station_endpoint(
    station_data: StationCreateNonAdmin,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle station pour la propre compagnie de l'utilisateur (réservé aux utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie')
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "creer_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'creer_stations' required"
        )

    # Ensure that only non-admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to non-admin users"
        )

    # Verify that the user belongs to a company
    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company"
        )

    # Automatically set the company and country IDs to match the user's
    user_compagnie_id = str(current_user.compagnie_id)

    # Fetch the company to get its country
    from services.structures_service import get_compagnie_by_id
    compagnie = get_compagnie_by_id(db, user_compagnie_id)
    if not compagnie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User's company not found"
        )

    user_pays_id = str(compagnie.pays_id) if compagnie.pays_id else None

    try:
        db_station = create_station(
            db,
            compagnie_id=user_compagnie_id,
            code=station_data.code,
            nom=station_data.nom,
            adresse=station_data.adresse,
            telephone=station_data.telephone,
            email=station_data.email,
            pays_id=user_pays_id
        )

        return StationResponse(
            id=str(db_station.id),
            compagnie_id=str(db_station.compagnie_id),
            code=db_station.code,
            nom=db_station.nom,
            adresse=db_station.adresse,
            telephone=db_station.telephone,
            email=db_station.email,
            pays_id=str(db_station.pays_id) if db_station.pays_id else None,
            statut=db_station.statut,
            created_at=db_station.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


# Create a new model for station creation without required compagnie_id and pays_id for non-admin users
from pydantic import BaseModel as PydanticBaseModel, Field
from typing import Optional

class StationCreateNonAdmin(PydanticBaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None


@router.get("/stations/{station_id}", response_model=StationResponse)
async def get_station_endpoint(
    station_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get station details by ID
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "lire_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'lire_stations' required"
        )

    station = get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    # Verify that non-admin users can only access stations for their own company
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # Using str() to ensure both values are properly compared as strings
        user_compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        station_compagnie_id = str(station.compagnie_id) if station.compagnie_id else None

        if station_compagnie_id != user_compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access stations for your own company"
            )

    return StationResponse(
        id=str(station.id),
        compagnie_id=str(station.compagnie_id),
        code=station.code,
        nom=station.nom,
        adresse=station.adresse,
        telephone=station.telephone,
        email=station.email,
        pays_id=str(station.pays_id) if station.pays_id else None,
        statut=station.statut,
        created_at=station.created_at.isoformat()
    )


@router.get("/stations", response_model=StationListResponse)
async def get_stations_list(
    compagnie_id: Optional[str] = Query(None, description="Filter by company ID"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    pays_id: Optional[str] = Query(None, description="Filter by country ID"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all stations with optional filters
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "lire_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'lire_stations' required"
        )

    # Non-admin users can only see stations from their own company
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # For non-admin users, only show stations from their company
        # Check if requested company ID matches user's company (if provided)
        if compagnie_id and compagnie_id != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access stations for your own company"
            )
        user_compagnie_id = current_user.compagnie_id
        stations_list = get_all_stations(
            db,
            compagnie_id=user_compagnie_id,  # Override any provided compagnie_id filter
            statut=statut,
            pays_id=pays_id
        )
    else:
        # Admin users can see all stations or filtered by compagnie_id if provided
        stations_list = get_all_stations(
            db,
            compagnie_id=compagnie_id,
            statut=statut,
            pays_id=pays_id
        )

    total = len(stations_list)

    # Apply pagination to the results
    paginated_stations = stations_list[offset:offset+limit]

    return StationListResponse(
        success=True,
        data=[
            StationResponse(
                id=str(station.id),
                compagnie_id=str(station.compagnie_id),
                code=station.code,
                nom=station.nom,
                adresse=station.adresse,
                telephone=station.telephone,
                email=station.email,
                pays_id=str(station.pays_id) if station.pays_id else None,
                statut=station.statut,
                created_at=station.created_at.isoformat()
            )
            for station in paginated_stations
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.put("/stations/{station_id}", response_model=StationResponse)
async def update_station_endpoint(
    station_id: str,
    station_data: StationUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a station
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "modifier_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'modifier_stations' required"
        )

    # Get the station to check if it belongs to the user's company
    station = get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    # Verify that non-admin users can only update stations for their own company
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # Using str() to ensure both values are properly compared as strings
        user_compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        station_compagnie_id = str(station.compagnie_id) if station.compagnie_id else None

        if station_compagnie_id != user_compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update stations for your own company"
            )

    updated_station = update_station(db, station_id, **station_data.dict(exclude_unset=True))
    if not updated_station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    return StationResponse(
        id=str(updated_station.id),
        compagnie_id=str(updated_station.compagnie_id),
        code=updated_station.code,
        nom=updated_station.nom,
        adresse=updated_station.adresse,
        telephone=updated_station.telephone,
        email=updated_station.email,
        pays_id=str(updated_station.pays_id) if updated_station.pays_id else None,
        statut=updated_station.statut,
        created_at=updated_station.created_at.isoformat()
    )


@router.post("/barremage-cuves", response_model=BarremageCuveResponse)
async def create_barremage_cuves_endpoint(
    barremage_data: BarremageCuveCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new barremage cuve entry
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    user_type = current_user.type_utilisateur
    # Vérifier la permission pour créer des barrements de cuves
    if not (has_permission(db, str(current_user.id), "barremage.creer") or is_admin_or_super_admin(user_type)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'barremage.creer' required"
        )

    # Vérifier que l'utilisateur appartient à la même compagnie que la station et la cuve
    from services.structures_service import get_station_by_id, get_cuve_by_id
    station = get_station_by_id(db, barremage_data.station_id)
    cuve = get_cuve_by_id(db, barremage_data.cuve_id)

    if not station or not cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station or cuve not found"
        )

    # Vérifier que la station et la cuve appartiennent à la même compagnie
    if str(station.compagnie_id) != str(cuve.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Station and cuve must belong to the same company"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(station.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    db_barremage = create_barremage_cuves(
        db,
        cuve_id=barremage_data.cuve_id,
        station_id=barremage_data.station_id,
        hauteur=barremage_data.hauteur,
        volume=barremage_data.volume,
        compagnie_id=str(station.compagnie_id)  # Utiliser la compagnie de la station
    )

    return BarremageCuveResponse(
        id=str(db_barremage.id),
        cuve_id=str(db_barremage.cuve_id),
        station_id=str(db_barremage.station_id),
        hauteur=float(db_barremage.hauteur),
        volume=float(db_barremage.volume),
        statut=db_barremage.statut,
        compagnie_id=str(db_barremage.compagnie_id),
        created_at=db_barremage.created_at.isoformat(),
        updated_at=db_barremage.updated_at.isoformat() if db_barremage.updated_at else None
    )


@router.get("/barremage-cuves", response_model=BarremageCuveListResponse)
async def get_barremage_cuves_list(
    cuve_id: Optional[str] = Query(None, description="Filter by cuve ID"),
    station_id: Optional[str] = Query(None, description="Filter by station ID"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all barremage cuve entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    user_type = current_user.type_utilisateur
    # Vérifier la permission pour lire les barrements de cuves
    if not (has_permission(db, str(current_user.id), "barremage.lire") or is_admin_or_super_admin(user_type)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'barremage.lire' required"
        )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Vérifier que seuls les utilisateurs admin ou ceux de la même compagnie peuvent accéder aux données
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        barremage_cuves_list = get_all_barremage_cuves(
            db,
            cuve_id=cuve_id,
            station_id=station_id,
            compagnie_id=user_company_id,
            statut=statut
        )
    else:
        # Les admins peuvent voir toutes les données
        barremage_cuves_list = get_all_barremage_cuves(
            db,
            cuve_id=cuve_id,
            station_id=station_id,
            statut=statut
        )

    total = len(barremage_cuves_list)

    # Appliquer la pagination
    paginated_barremage = barremage_cuves_list[offset:offset+limit]

    return BarremageCuveListResponse(
        success=True,
        data=[
            BarremageCuveResponse(
                id=str(barremage.id),
                cuve_id=str(barremage.cuve_id),
                station_id=str(barremage.station_id),
                hauteur=float(barremage.hauteur),
                volume=float(barremage.volume),
                statut=barremage.statut,
                compagnie_id=str(barremage.compagnie_id),
                created_at=barremage.created_at.isoformat(),
                updated_at=barremage.updated_at.isoformat() if barremage.updated_at else None
            )
            for barremage in paginated_barremage
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.get("/barremage-cuves/{barremage_id}", response_model=BarremageCuveResponse)
async def get_barremage_cuves_by_id_endpoint(
    barremage_id: str,
    current_user: Utilisateur = Depends(create_permission_dependency("barremage.lire")),
    db: Session = Depends(get_db)
):
    """
    Get a specific barremage cuve entry by ID
    """
    from utils.access_control import is_admin_or_super_admin
    from services.structures_service import get_barremage_cuves_by_id

    barremage = get_barremage_cuves_by_id(db, barremage_id)
    if not barremage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barremage cuve entry not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut accéder à cette donnée (mêmes droits que pour la lecture)
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        if str(barremage.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this barremage cuve entry is not authorized for this user"
            )

    return BarremageCuveResponse(
        id=str(barremage.id),
        cuve_id=str(barremage.cuve_id),
        station_id=str(barremage.station_id),
        hauteur=float(barremage.hauteur),
        volume=float(barremage.volume),
        statut=barremage.statut,
        compagnie_id=str(barremage.compagnie_id),
        created_at=barremage.created_at.isoformat(),
        updated_at=barremage.updated_at.isoformat() if barremage.updated_at else None
    )


@router.put("/barremage-cuves/{barremage_id}", response_model=BarremageCuveResponse)
async def update_barremage_cuves_endpoint(
    barremage_id: str,
    barremage_data: BarremageCuveUpdate,
    current_user: Utilisateur = Depends(create_permission_dependency("barremage.modifier")),
    db: Session = Depends(get_db)
):
    """
    Update a specific barremage cuve entry
    """
    from utils.access_control import is_admin_or_super_admin
    from services.structures_service import get_barremage_cuves_by_id

    barremage = get_barremage_cuves_by_id(db, barremage_id)
    if not barremage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barremage cuve entry not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut modifier cette donnée
    if not is_admin_or_super_admin(user_type):
        if str(barremage.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to modify this barremage cuve entry is not authorized for this user"
            )

    # Mettre à jour l'entrée
    updated_barremage = update_barremage_cuves(db, barremage_id, **barremage_data.dict(exclude_unset=True))
    if not updated_barremage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to update barremage cuve entry"
        )

    return BarremageCuveResponse(
        id=str(updated_barremage.id),
        cuve_id=str(updated_barremage.cuve_id),
        station_id=str(updated_barremage.station_id),
        hauteur=float(updated_barremage.hauteur),
        volume=float(updated_barremage.volume),
        statut=updated_barremage.statut,
        compagnie_id=str(updated_barremage.compagnie_id),
        created_at=updated_barremage.created_at.isoformat(),
        updated_at=updated_barremage.updated_at.isoformat() if updated_barremage.updated_at else None
    )


@router.delete("/barremage-cuves/{barremage_id}")
async def delete_barremage_cuves_endpoint(
    barremage_id: str,
    current_user: Utilisateur = Depends(create_permission_dependency("barremage.supprimer")),
    db: Session = Depends(get_db)
):
    """
    Delete a specific barremage cuve entry
    """
    from utils.access_control import is_admin_or_super_admin
    from services.structures_service import get_barremage_cuves_by_id

    barremage = get_barremage_cuves_by_id(db, barremage_id)
    if not barremage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barremage cuve entry not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut supprimer cette donnée
    if not is_admin_or_super_admin(user_type):
        if str(barremage.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to delete this barremage cuve entry is not authorized for this user"
            )

    success = delete_barremage_cuves(db, barremage_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to delete barremage cuve entry"
        )

    return {"success": True, "message": "Barremage cuve entry deleted successfully"}


@router.post("/cuves", response_model=CuveResponse)
async def create_cuve_endpoint(
    cuve_data: CuveCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new cuve
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    user_type = current_user.type_utilisateur
    # Vérifier la permission pour créer des cuves
    if not (has_permission(db, str(current_user.id), "cuves.creer") or is_admin_or_super_admin(user_type)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'cuves.creer' required"
        )

    # Vérifier que la station existe
    station = get_station_by_id(db, cuve_data.station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(station.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Déterminer la compagnie en fonction du type d'utilisateur
    if is_admin_or_super_admin(user_type):
        compagnie_id = str(station.compagnie_id)
    else:
        compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Si carburant_id est fourni, vérifier qu'il existe et qu'il appartient à la même compagnie
    if cuve_data.carburant_id:
        carburant = get_carburant_by_id(db, cuve_data.carburant_id)
        if not carburant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carburant not found"
            )
        # Vérifier que le carburant appartient à la même compagnie que la station
        if not is_admin_or_super_admin(user_type) and str(carburant.compagnie_id) != compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this carburant is not authorized for this user"
            )

    db_cuve = create_cuve(
        db,
        station_id=cuve_data.station_id,
        code=cuve_data.code,
        capacite=cuve_data.capacite,
        carburant_id=cuve_data.carburant_id,
        compagnie_id=compagnie_id,
        temperature=cuve_data.temperature,
        statut=cuve_data.statut
    )

    return CuveResponse(
        id=str(db_cuve.id),
        station_id=str(db_cuve.station_id),
        code=db_cuve.code,
        capacite=float(db_cuve.capacite),
        carburant_id=str(db_cuve.carburant_id) if db_cuve.carburant_id else None,
        compagnie_id=str(db_cuve.compagnie_id),
        temperature=float(db_cuve.temperature),
        statut=db_cuve.statut,
        created_at=db_cuve.created_at.isoformat(),
        updated_at=db_cuve.updated_at.isoformat() if db_cuve.updated_at else None
    )


@router.get("/cuves", response_model=CuveListResponse)
async def get_cuves_list(
    station_id: Optional[str] = Query(None, description="Filter by station ID"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all cuves with optional filters
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    user_type = current_user.type_utilisateur
    # Vérifier la permission pour lire les cuves
    if not (has_permission(db, str(current_user.id), "cuves.lire") or is_admin_or_super_admin(user_type)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'cuves.lire' required"
        )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer les cuves avec ou sans filtre de compagnie
    if is_admin_or_super_admin(user_type):
        # Les admins peuvent voir toutes les cuves
        cuves_list = get_all_cuves(
            db,
            station_id=station_id,
            statut=statut
        )
    else:
        # Les utilisateurs non admin ne peuvent voir que les cuves de leur compagnie
        cuves_list = get_all_cuves(
            db,
            station_id=station_id,
            compagnie_id=user_company_id,
            statut=statut
        )

    total = len(cuves_list)

    # Appliquer la pagination
    paginated_cuves = cuves_list[offset:offset+limit]

    return CuveListResponse(
        success=True,
        data=[
            CuveResponse(
                id=str(cuve.id),
                station_id=str(cuve.station_id),
                code=cuve.code,
                capacite=float(cuve.capacite),
                carburant_id=str(cuve.carburant_id) if cuve.carburant_id else None,
                compagnie_id=str(cuve.compagnie_id),
                temperature=float(cuve.temperature),
                statut=cuve.statut,
                created_at=cuve.created_at.isoformat(),
                updated_at=cuve.updated_at.isoformat() if cuve.updated_at else None
            )
            for cuve in paginated_cuves
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.get("/cuves/{cuve_id}", response_model=CuveResponse)
async def get_cuve_by_id_endpoint(
    cuve_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific cuve by ID
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    user_type = current_user.type_utilisateur
    # Vérifier la permission pour lire les cuves
    if not (has_permission(db, str(current_user.id), "cuves.lire") or is_admin_or_super_admin(user_type)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'cuves.lire' required"
        )

    cuve = get_cuve_by_id(db, cuve_id)
    if not cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuve not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut accéder à cette cuve
    if not is_admin_or_super_admin(user_type):
        if current_user.compagnie_id and str(cuve.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this cuve is not authorized for this user"
            )

    return CuveResponse(
        id=str(cuve.id),
        station_id=str(cuve.station_id),
        code=cuve.code,
        capacite=float(cuve.capacite),
        carburant_id=str(cuve.carburant_id) if cuve.carburant_id else None,
        compagnie_id=str(cuve.compagnie_id),
        temperature=float(cuve.temperature),
        statut=cuve.statut,
        created_at=cuve.created_at.isoformat(),
        updated_at=cuve.updated_at.isoformat() if cuve.updated_at else None
    )


@router.put("/cuves/{cuve_id}", response_model=CuveResponse)
async def update_cuve_endpoint(
    cuve_id: str,
    cuve_data: CuveUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific cuve
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    user_type = current_user.type_utilisateur
    # Vérifier la permission pour modifier les cuves
    if not (has_permission(db, str(current_user.id), "cuves.modifier") or is_admin_or_super_admin(user_type)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'cuves.modifier' required"
        )
    from services.structures_service import get_cuve_by_id

    cuve = get_cuve_by_id(db, cuve_id)
    if not cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuve not found"
        )

    user_type = current_user.type_utilisateur

    # Vérifier que l'utilisateur peut modifier cette cuve
    if not is_admin_or_super_admin(user_type):
        if str(cuve.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to modify this cuve is not authorized for this user"
            )

    # Vérifier la validité des données liées si elles sont mises à jour
    update_data = cuve_data.dict(exclude_unset=True)
    if 'carburant_id' in update_data and update_data['carburant_id']:
        carburant = get_carburant_by_id(db, update_data['carburant_id'])
        if not carburant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carburant not found"
            )
        if not is_admin_or_super_admin(user_type) and current_user.compagnie_id and str(carburant.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this carburant is not authorized for this user"
            )

    # Mettre à jour la cuve
    updated_cuve = update_cuve(db, cuve_id, **update_data)
    if not updated_cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to update cuve"
        )

    return CuveResponse(
        id=str(updated_cuve.id),
        station_id=str(updated_cuve.station_id),
        code=updated_cuve.code,
        capacite=float(updated_cuve.capacite),
        carburant_id=str(updated_cuve.carburant_id) if updated_cuve.carburant_id else None,
        compagnie_id=str(updated_cuve.compagnie_id),
        temperature=float(updated_cuve.temperature),
        statut=updated_cuve.statut,
        created_at=updated_cuve.created_at.isoformat(),
        updated_at=updated_cuve.updated_at.isoformat() if updated_cuve.updated_at else None
    )


@router.delete("/cuves/{cuve_id}")
async def delete_cuve_endpoint(
    cuve_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific cuve
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    user_type = current_user.type_utilisateur
    # Vérifier la permission pour supprimer des cuves
    if not (has_permission(db, str(current_user.id), "cuves.supprimer") or is_admin_or_super_admin(user_type)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'cuves.supprimer' required"
        )
    from services.structures_service import get_cuve_by_id

    cuve = get_cuve_by_id(db, cuve_id)
    if not cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuve not found"
        )

    user_type = current_user.type_utilisateur

    # Vérifier que l'utilisateur peut supprimer cette cuve
    if not is_admin_or_super_admin(user_type):
        if current_user.compagnie_id and str(cuve.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to delete this cuve is not authorized for this user"
            )

    # Vérifier s'il y a des dépendances (ex: barremage, pistolets, etc.) avant suppression
    # Pour l'instant, on suppose que la suppression est possible si l'utilisateur a les droits

    success = delete_cuve(db, cuve_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to delete cuve"
        )

    return {"success": True, "message": "Cuve deleted successfully"}


@router.post("/carburants", response_model=CarburantResponse)
async def create_carburant_endpoint(
    carburant_data: CarburantCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("carburants.creer")),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau carburant (réservé aux utilisateurs 'administrateur' et 'super_administrateur')
    Seul ce endpoint permet de spécifier explicitement le 'compagnie_id'
    """
    from utils.access_control import is_admin_or_super_admin

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur appartient à la même compagnie que spécifiée
    if not is_admin_or_super_admin(user_type):
        if str(carburant_data.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to create carburant for this company is not authorized for this user"
            )

    # Vérifier si un carburant avec le même code existe déjà
    existing_carburant = get_carburant_by_code(db, carburant_data.code)
    if existing_carburant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Carburant with code {carburant_data.code} already exists"
        )

    db_carburant = create_carburant(
        db,
        code=carburant_data.code,
        libelle=carburant_data.libelle,
        type_carburant=carburant_data.type,
        compagnie_id=carburant_data.compagnie_id,
        prix_achat=carburant_data.prix_achat,
        prix_vente=carburant_data.prix_vente,
        statut=carburant_data.statut
    )

    return CarburantResponse(
        id=str(db_carburant.id),
        code=db_carburant.code,
        libelle=db_carburant.libelle,
        type=db_carburant.type,
        compagnie_id=str(db_carburant.compagnie_id),
        prix_achat=float(db_carburant.prix_achat) if db_carburant.prix_achat else 0.0,
        prix_vente=float(db_carburant.prix_vente) if db_carburant.prix_vente else 0.0,
        statut=db_carburant.statut,
        created_at=db_carburant.created_at.isoformat(),
        updated_at=db_carburant.updated_at.isoformat() if db_carburant.updated_at else None
    )


@router.post("/my-carburants", response_model=CarburantResponse)
async def create_my_carburant_endpoint(
    carburant_data: CarburantCreateNonAdmin,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau carburant pour la propre compagnie de l'utilisateur (réservé aux utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie')
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "carburants.creer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'carburants.creer' required"
        )

    # Ensure that only non-admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to non-admin users"
        )

    # Verify that the user belongs to a company
    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company"
        )

    # Automatically set the company ID to match the user's
    user_compagnie_id = str(current_user.compagnie_id)

    # Vérifier si un carburant avec le même code existe déjà pour cette compagnie
    existing_carburant = get_carburant_by_code(db, carburant_data.code)
    if existing_carburant and str(existing_carburant.compagnie_id) == user_compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Carburant with code {carburant_data.code} already exists for this company"
        )

    db_carburant = create_carburant(
        db,
        code=carburant_data.code,
        libelle=carburant_data.libelle,
        type_carburant=carburant_data.type,
        compagnie_id=user_compagnie_id,
        prix_achat=carburant_data.prix_achat,
        prix_vente=carburant_data.prix_vente,
        statut=carburant_data.statut
    )

    return CarburantResponse(
        id=str(db_carburant.id),
        code=db_carburant.code,
        libelle=db_carburant.libelle,
        type=db_carburant.type,
        compagnie_id=str(db_carburant.compagnie_id),
        prix_achat=float(db_carburant.prix_achat) if db_carburant.prix_achat else 0.0,
        prix_vente=float(db_carburant.prix_vente) if db_carburant.prix_vente else 0.0,
        statut=db_carburant.statut,
        created_at=db_carburant.created_at.isoformat(),
        updated_at=db_carburant.updated_at.isoformat() if db_carburant.updated_at else None
    )


@router.get("/carburants", response_model=CarburantListResponse)
async def get_carburants_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("carburants.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all carburants with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Déterminer la compagnie en fonction du type d'utilisateur
    if not is_admin_or_super_admin(user_type):
        compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        carburants_list = get_all_carburants(db, compagnie_id=compagnie_id, statut=statut)
    else:
        # Les admins peuvent voir tous les carburants avec filtres optionnels
        carburants_list = get_all_carburants(db, statut=statut)

    total = len(carburants_list)

    # Appliquer la pagination
    paginated_carburants = carburants_list[offset:offset+limit]

    return CarburantListResponse(
        success=True,
        data=[
            CarburantResponse(
                id=str(carburant.id),
                code=carburant.code,
                libelle=carburant.libelle,
                type=carburant.type,
                compagnie_id=str(carburant.compagnie_id),
                prix_achat=float(carburant.prix_achat) if carburant.prix_achat else 0.0,
                prix_vente=float(carburant.prix_vente) if carburant.prix_vente else 0.0,
                statut=carburant.statut,
                created_at=carburant.created_at.isoformat(),
                updated_at=carburant.updated_at.isoformat() if carburant.updated_at else None
            )
            for carburant in paginated_carburants
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.get("/carburants/{carburant_id}", response_model=CarburantResponse)
@prohibit_super_admin_access
async def get_carburant_by_id_endpoint(
    carburant_id: str,
    current_user: Utilisateur = Depends(create_permission_dependency("carburants.lire")),
    db: Session = Depends(get_db)
):
    """
    Get a specific carburant by ID
    """
    from services.structures_service import get_carburant_by_id
    from utils.access_control import verify_entity_access

    carburant = get_carburant_by_id(db, carburant_id)
    if not carburant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carburant not found"
        )

    # Verify that the user has access to this carburant entity
    verify_entity_access(db, current_user, carburant, "carburant")

    return CarburantResponse(
        id=str(carburant.id),
        code=carburant.code,
        libelle=carburant.libelle,
        type=carburant.type,
        compagnie_id=str(carburant.compagnie_id),
        prix_achat=float(carburant.prix_achat) if carburant.prix_achat else 0.0,
        prix_vente=float(carburant.prix_vente) if carburant.prix_vente else 0.0,
        statut=carburant.statut,
        created_at=carburant.created_at.isoformat(),
        updated_at=carburant.updated_at.isoformat() if carburant.updated_at else None
    )


@router.put("/carburants/{carburant_id}", response_model=CarburantResponse)
async def update_carburant_endpoint(
    carburant_id: str,
    carburant_data: CarburantUpdate,
    current_user: Utilisateur = Depends(create_permission_dependency("carburants.modifier")),
    db: Session = Depends(get_db)
):
    """
    Update a specific carburant
    """
    from utils.access_control import is_admin_or_super_admin
    from services.structures_service import get_carburant_by_id

    carburant = get_carburant_by_id(db, carburant_id)
    if not carburant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carburant not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut modifier ce carburant
    if not is_admin_or_super_admin(user_type):
        if str(carburant.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to modify this carburant is not authorized for this user"
            )

    # Préparer les données de mise à jour
    update_data = carburant_data.dict(exclude_unset=True)

    # Mettre à jour le carburant
    updated_carburant = update_carburant(db, carburant_id, **update_data)
    if not updated_carburant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to update carburant"
        )

    return CarburantResponse(
        id=str(updated_carburant.id),
        code=updated_carburant.code,
        libelle=updated_carburant.libelle,
        type=updated_carburant.type,
        compagnie_id=str(updated_carburant.compagnie_id),
        prix_achat=float(updated_carburant.prix_achat) if updated_carburant.prix_achat else 0.0,
        prix_vente=float(updated_carburant.prix_vente) if updated_carburant.prix_vente else 0.0,
        statut=updated_carburant.statut,
        created_at=updated_carburant.created_at.isoformat(),
        updated_at=updated_carburant.updated_at.isoformat() if updated_carburant.updated_at else None
    )


@router.delete("/carburants/{carburant_id}")
async def delete_carburant_endpoint(
    carburant_id: str,
    current_user: Utilisateur = Depends(create_permission_dependency("carburants.supprimer")),
    db: Session = Depends(get_db)
):
    """
    Delete a specific carburant
    """
    from utils.access_control import is_admin_or_super_admin
    from services.structures_service import get_carburant_by_id

    carburant = get_carburant_by_id(db, carburant_id)
    if not carburant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carburant not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut supprimer ce carburant
    if not is_admin_or_super_admin(user_type):
        if current_user.compagnie_id and str(carburant.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to delete this carburant is not authorized for this user"
            )

    success = delete_carburant(db, carburant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to delete carburant"
        )

    return {"success": True, "message": "Carburant deleted successfully"}


@router.post("/articles", response_model=ArticleResponse)
@prohibit_super_admin_access
async def create_article_endpoint(
    article_data: ArticleCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("articles.creer")),
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel article (réservé aux utilisateurs 'administrateur' et 'super_administrateur')
    Seul ce endpoint permet de spécifier explicitement le 'compagnie_id'
    """
    from utils.access_control import is_admin_or_super_admin

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur appartient à la même compagnie que spécifiée
    if not is_admin_or_super_admin(user_type):
        if str(article_data.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to create article for this company is not authorized for this user"
            )

    # Vérifier si un article avec le même code existe déjà
    existing_article = get_article_by_id(db, article_data.code)
    if existing_article:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Article with code {article_data.code} already exists"
        )

    db_article = create_article(
        db,
        code=article_data.code,
        libelle=article_data.libelle,
        codebarre=article_data.codebarre,
        famille_id=article_data.famille_id,
        unite=article_data.unite,
        compagnie_id=article_data.compagnie_id,
        type_article=article_data.type_article,
        prix_achat=article_data.prix_achat,
        prix_vente=article_data.prix_vente,
        tva=article_data.tva,
        stock_minimal=article_data.stock_minimal,
        statut=article_data.statut
    )

    return ArticleResponse(
        id=str(db_article.id),
        code=db_article.code,
        libelle=db_article.libelle,
        codebarre=db_article.codebarre,
        famille_id=str(db_article.famille_id) if db_article.famille_id else None,
        unite=db_article.unite,
        compagnie_id=str(db_article.compagnie_id),
        type_article=db_article.type_article,
        prix_achat=float(db_article.prix_achat) if db_article.prix_achat else 0.0,
        prix_vente=float(db_article.prix_vente) if db_article.prix_vente else 0.0,
        tva=float(db_article.tva) if db_article.tva else 0.0,
        stock_minimal=float(db_article.stock_minimal) if db_article.stock_minimal else 0.0,
        statut=db_article.statut,
        created_at=db_article.created_at.isoformat(),
        updated_at=db_article.updated_at.isoformat() if db_article.updated_at else None
    )


@router.post("/my-articles", response_model=ArticleResponse)
async def create_my_article_endpoint(
    article_data: ArticleCreateNonAdmin,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel article pour la propre compagnie de l'utilisateur (réservé aux utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie')
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "articles.creer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'articles.creer' required"
        )

    # Ensure that only non-admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to non-admin users"
        )

    # Verify that the user belongs to a company
    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company"
        )

    # Automatically set the company ID to match the user's
    user_compagnie_id = str(current_user.compagnie_id)

    # Vérifier si un article avec le même code existe déjà pour cette compagnie
    existing_article = get_article_by_code(db, article_data.code, user_compagnie_id)
    if existing_article:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Article with code {article_data.code} already exists for this company"
        )

    db_article = create_article(
        db,
        code=article_data.code,
        libelle=article_data.libelle,
        codebarre=article_data.codebarre,
        famille_id=article_data.famille_id,
        unite=article_data.unite,
        compagnie_id=user_compagnie_id,
        type_article=article_data.type_article,
        prix_achat=article_data.prix_achat,
        prix_vente=article_data.prix_vente,
        tva=article_data.tva,
        stock_minimal=article_data.stock_minimal,
        statut=article_data.statut
    )

    return ArticleResponse(
        id=str(db_article.id),
        code=db_article.code,
        libelle=db_article.libelle,
        codebarre=db_article.codebarre,
        famille_id=str(db_article.famille_id) if db_article.famille_id else None,
        unite=db_article.unite,
        compagnie_id=str(db_article.compagnie_id),
        type_article=db_article.type_article,
        prix_achat=float(db_article.prix_achat) if db_article.prix_achat else 0.0,
        prix_vente=float(db_article.prix_vente) if db_article.prix_vente else 0.0,
        tva=float(db_article.tva) if db_article.tva else 0.0,
        stock_minimal=float(db_article.stock_minimal) if db_article.stock_minimal else 0.0,
        statut=db_article.statut,
        created_at=db_article.created_at.isoformat(),
        updated_at=db_article.updated_at.isoformat() if db_article.updated_at else None
    )


@router.get("/articles", response_model=ArticleListResponse)
async def get_articles_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les articles avec des filtres optionnels
    Pour les utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie', seuls les articles de leur propre compagnie sont retournés
    Les administrateurs peuvent voir tous les articles s'ils ont la permission
    """
    from utils.access_control import is_admin_or_super_admin, has_permission
    from utils.access_control import prohibit_super_admin_access

    # Check if super admin access is prohibited
    if is_admin_or_super_admin(current_user.type_utilisateur) and current_user.type_utilisateur == "super_administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super administrators are not allowed to perform daily operations"
        )

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "articles.lire"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'articles.lire' required"
        )

    user_type = current_user.type_utilisateur

    # Déterminer la compagnie en fonction du type d'utilisateur
    if not is_admin_or_super_admin(user_type):
        compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        articles_list = get_all_articles(db, compagnie_id=compagnie_id, statut=statut)
    else:
        # Les admins peuvent voir tous les articles avec filtres optionnels
        articles_list = get_all_articles(db, statut=statut)

    total = len(articles_list)

    # Appliquer la pagination
    paginated_articles = articles_list[offset:offset+limit]

    return ArticleListResponse(
        success=True,
        data=[
            ArticleResponse(
                id=str(article.id),
                code=article.code,
                libelle=article.libelle,
                codebarre=article.codebarre,
                famille_id=str(article.famille_id) if article.famille_id else None,
                unite=article.unite,
                compagnie_id=str(article.compagnie_id),
                type_article=article.type_article,
                prix_achat=float(article.prix_achat) if article.prix_achat else 0.0,
                prix_vente=float(article.prix_vente) if article.prix_vente else 0.0,
                tva=float(article.tva) if article.tva else 0.0,
                stock_minimal=float(article.stock_minimal) if article.stock_minimal else 0.0,
                statut=article.statut,
                created_at=article.created_at.isoformat(),
                updated_at=article.updated_at.isoformat() if article.updated_at else None
            )
            for article in paginated_articles
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


logger.info("Endpoints pour les cuves enregistrés avec succès")
logger.info("Endpoints pour les carburants enregistrés avec succès")
logger.info("Endpoints pour les articles enregistrés avec succès")


@router.post("/import-barremage-excel")
@require_permission("barremage.importer")
async def import_barremage_excel_endpoint(
    cuve_id: str = Form(..., description="ID de la cuve cible"),
    file: UploadFile = File(...),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import barremage data from an Excel file
    Le station_id est automatiquement déduit du cuve_id
    Le fichier doit contenir les colonnes 'hauteur' et 'volume'
    """
    from utils.access_control import is_admin_or_super_admin
    from services.structures_service import get_cuve_by_id
    user_type = current_user.type_utilisateur

    # Vérifier que l'utilisateur est autorisé à importer des données
    # Seuls les gérants de compagnie et les administrateurs peuvent importer
    if is_admin_or_super_admin(user_type):
        # Les admins peuvent importer
        pass
    elif user_type == "gerant_compagnie":
        # Les gérants de compagnie peuvent importer
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à importer des données"
        )

    # Récupérer la cuve pour en déduire la station
    cuve = get_cuve_by_id(db, cuve_id)
    if not cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuve avec ID {cuve_id} non trouvée"
        )

    station_id = str(cuve.station_id)
    result = import_barremage_from_excel(db, file, current_user, cuve_id, station_id)
    return result


@router.post("/pompes", response_model=PompeResponse)
@require_permission("pompes.creer")
async def create_pompe_endpoint(
    pompe_data: PompeCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new pompe
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Vérifier que la station existe
    station = get_station_by_id(db, pompe_data.station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(station.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    db_pompe = create_pompe(
        db,
        station_id=pompe_data.station_id,
        code=pompe_data.code,
        compagnie_id=str(station.compagnie_id)  # Utiliser la compagnie de la station
    )

    return PompeResponse(
        id=str(db_pompe.id),
        station_id=str(db_pompe.station_id),
        code=db_pompe.code,
        compagnie_id=str(db_pompe.compagnie_id),
        statut=db_pompe.statut,
        created_at=db_pompe.created_at.isoformat()
    )


@router.get("/pompes", response_model=PompeListResponse)
@require_permission("pompes.lire")
async def get_pompes_list(
    station_id: Optional[str] = Query(None, description="Filter by station ID"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pompes with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Vérifier que seuls les utilisateurs admin ou ceux de la même compagnie peuvent accéder aux données
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        pompes_list = get_all_pompes(
            db,
            station_id=station_id,
            compagnie_id=user_company_id,
            statut=statut
        )
    else:
        # Les admins peuvent voir toutes les données
        pompes_list = get_all_pompes(
            db,
            station_id=station_id,
            statut=statut
        )

    total = len(pompes_list)

    # Appliquer la pagination
    paginated_pompes = pompes_list[offset:offset+limit]

    return PompeListResponse(
        success=True,
        data=[
            PompeResponse(
                id=str(pompe.id),
                station_id=str(pompe.station_id),
                code=pompe.code,
                compagnie_id=str(pompe.compagnie_id),
                statut=pompe.statut,
                created_at=pompe.created_at.isoformat()
            )
            for pompe in paginated_pompes
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.get("/pompes/{pompe_id}", response_model=PompeResponse)
@require_permission("pompes.lire")
async def get_pompe_by_id_endpoint(
    pompe_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific pompe by ID
    """
    from utils.access_control import is_admin_or_super_admin

    pompe = get_pompe_by_id(db, pompe_id)
    if not pompe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pompe not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut accéder à cette donnée (mêmes droits que pour la lecture)
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        if str(pompe.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this pompe is not authorized for this user"
            )

    return PompeResponse(
        id=str(pompe.id),
        station_id=str(pompe.station_id),
        code=pompe.code,
        compagnie_id=str(pompe.compagnie_id),
        statut=pompe.statut,
        created_at=pompe.created_at.isoformat()
    )


@router.put("/pompes/{pompe_id}", response_model=PompeResponse)
@require_permission("pompes.modifier")
async def update_pompe_endpoint(
    pompe_id: str,
    pompe_data: PompeUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific pompe
    """
    from utils.access_control import is_admin_or_super_admin

    pompe = get_pompe_by_id(db, pompe_id)
    if not pompe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pompe not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut modifier cette donnée
    if not is_admin_or_super_admin(user_type):
        if str(pompe.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to modify this pompe is not authorized for this user"
            )

    # Mettre à jour l'entrée
    updated_pompe = update_pompe(db, pompe_id, **pompe_data.dict(exclude_unset=True))
    if not updated_pompe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to update pompe"
        )

    return PompeResponse(
        id=str(updated_pompe.id),
        station_id=str(updated_pompe.station_id),
        code=updated_pompe.code,
        compagnie_id=str(updated_pompe.compagnie_id),
        statut=updated_pompe.statut,
        created_at=updated_pompe.created_at.isoformat()
    )


@router.delete("/pompes/{pompe_id}")
@require_permission("pompes.supprimer")
async def delete_pompe_endpoint(
    pompe_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific pompe
    """
    from utils.access_control import is_admin_or_super_admin

    pompe = get_pompe_by_id(db, pompe_id)
    if not pompe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pompe not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut supprimer cette donnée
    if not is_admin_or_super_admin(user_type):
        if str(pompe.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to delete this pompe is not authorized for this user"
            )

    success = delete_pompe(db, pompe_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to delete pompe"
        )

    return {"success": True, "message": "Pompe deleted successfully"}


@router.post("/pistolets", response_model=PistoletResponse)
@require_permission("pistolets.creer")
@prohibit_super_admin_access
async def create_pistolet_endpoint(
    pistolet_data: PistoletCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new pistolet
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Vérifier que la pompe et la cuve existent
    from services.structures_service import get_pompe_by_id, get_cuve_by_id
    pompe = get_pompe_by_id(db, pistolet_data.pompe_id)
    cuve = get_cuve_by_id(db, pistolet_data.cuve_id)

    if not pompe or not cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pompe or cuve not found"
        )

    # Vérifier que la pompe et la cuve appartiennent à la même compagnie
    if str(pompe.compagnie_id) != str(cuve.compagnie_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pompe and cuve must belong to the same company"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pompe.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    db_pistolet = create_pistolet(
        db,
        code=pistolet_data.code,
        pompe_id=pistolet_data.pompe_id,
        cuve_id=pistolet_data.cuve_id,
        index_initiale=pistolet_data.index_initiale,
        compagnie_id=str(pompe.compagnie_id)  # Utiliser la compagnie de la pompe
    )

    return PistoletResponse(
        id=str(db_pistolet.id),
        code=db_pistolet.code,
        pompe_id=str(db_pistolet.pompe_id),
        cuve_id=str(db_pistolet.cuve_id),
        index_initiale=float(db_pistolet.index_initiale),
        compagnie_id=str(db_pistolet.compagnie_id),
        statut=db_pistolet.statut,
        created_at=db_pistolet.created_at.isoformat()
    )


@router.post("/my-pistolets", response_model=PistoletResponse)
async def create_my_pistolet_endpoint(
    pistolet_data: PistoletCreateNonAdmin,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau pistolet pour la propre compagnie de l'utilisateur (réservé aux utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie')
    Le pompe_id est optionnel - s'il n'est pas fourni, le pistolet est créé sans association à une pompe
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "pistolets.creer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'pistolets.creer' required"
        )

    # Ensure that only non-admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to non-admin users"
        )

    # Verify that the user belongs to a company
    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company"
        )

    user_compagnie_id = str(current_user.compagnie_id)

    # Vérifier que la cuve existe et qu'elle appartient à la compagnie de l'utilisateur
    from services.structures_service import get_cuve_by_id
    cuve = get_cuve_by_id(db, pistolet_data.cuve_id)
    if not cuve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuve not found"
        )

    if str(cuve.compagnie_id) != user_compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this cuve is not authorized for this user"
        )

    # Vérifier la pompe si elle est fournie
    pompe = None
    if pistolet_data.pompe_id:
        from services.structures_service import get_pompe_by_id
        pompe = get_pompe_by_id(db, pistolet_data.pompe_id)
        if not pompe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pompe not found"
            )

        # Vérifier que la pompe appartient à la même compagnie que la cuve
        if str(pompe.compagnie_id) != str(cuve.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pompe and cuve must belong to the same company"
            )

    # Créer le pistolet
    if pompe:
        # Si une pompe est spécifiée, utiliser la compagnie de la pompe (qui est la même que celle de la cuve)
        compagnie_id_to_use = str(pompe.compagnie_id)
    else:
        # Si aucune pompe n'est spécifiée, utiliser directement la compagnie de l'utilisateur
        compagnie_id_to_use = user_compagnie_id

    db_pistolet = create_pistolet(
        db,
        code=pistolet_data.code,
        pompe_id=pistolet_data.pompe_id,  # Peut être None
        cuve_id=pistolet_data.cuve_id,
        index_initiale=pistolet_data.index_initiale,
        compagnie_id=compagnie_id_to_use
    )

    return PistoletResponse(
        id=str(db_pistolet.id),
        code=db_pistolet.code,
        pompe_id=str(db_pistolet.pompe_id) if db_pistolet.pompe_id else None,
        cuve_id=str(db_pistolet.cuve_id),
        index_initiale=float(db_pistolet.index_initiale),
        compagnie_id=str(db_pistolet.compagnie_id),
        statut=db_pistolet.statut,
        created_at=db_pistolet.created_at.isoformat()
    )


@router.get("/pistolets", response_model=PistoletListResponse)
async def get_pistolets_list(
    pompe_id: Optional[str] = Query(None, description="Filter by pompe ID"),
    cuve_id: Optional[str] = Query(None, description="Filter by cuve ID"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pistolets with optional filters
    """
    from utils.access_control import is_admin_or_super_admin, has_permission
    from utils.access_control import prohibit_super_admin_access

    # Check if super admin access is prohibited
    if is_admin_or_super_admin(current_user.type_utilisateur) and current_user.type_utilisateur == "super_administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super administrators are not allowed to perform daily operations"
        )

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "pistolets.lire"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'pistolets.lire' required"
        )

    user_type = current_user.type_utilisateur

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Vérifier que seuls les utilisateurs admin ou ceux de la même compagnie peuvent accéder aux données
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        pistolets_list = get_all_pistolets(
            db,
            pompe_id=pompe_id,
            cuve_id=cuve_id,
            compagnie_id=user_company_id,
            statut=statut
        )
    else:
        # Les admins peuvent voir toutes les données
        pistolets_list = get_all_pistolets(
            db,
            pompe_id=pompe_id,
            cuve_id=cuve_id,
            statut=statut
        )

    total = len(pistolets_list)

    # Appliquer la pagination
    paginated_pistolets = pistolets_list[offset:offset+limit]

    return PistoletListResponse(
        success=True,
        data=[
            PistoletResponse(
                id=str(pistolet.id),
                code=pistolet.code,
                pompe_id=str(pistolet.pompe_id),
                cuve_id=str(pistolet.cuve_id),
                index_initiale=float(pistolet.index_initiale),
                compagnie_id=str(pistolet.compagnie_id),
                statut=pistolet.statut,
                created_at=pistolet.created_at.isoformat()
            )
            for pistolet in paginated_pistolets
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.get("/pistolets/{pistolet_id}", response_model=PistoletResponse)
@require_permission("pistolets.lire")
@prohibit_super_admin_access
async def get_pistolet_by_id_endpoint(
    pistolet_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific pistolet by ID
    """
    from utils.access_control import is_admin_or_super_admin

    pistolet = get_pistolet_by_id(db, pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut accéder à cette donnée (mêmes droits que pour la lecture)
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this pistolet is not authorized for this user"
            )

    return PistoletResponse(
        id=str(pistolet.id),
        code=pistolet.code,
        pompe_id=str(pistolet.pompe_id),
        cuve_id=str(pistolet.cuve_id),
        index_initiale=float(pistolet.index_initiale),
        compagnie_id=str(pistolet.compagnie_id),
        statut=pistolet.statut,
        created_at=pistolet.created_at.isoformat()
    )


@router.put("/pistolets/{pistolet_id}", response_model=PistoletResponse)
@require_permission("pistolets.modifier")
async def update_pistolet_endpoint(
    pistolet_id: str,
    pistolet_data: PistoletUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific pistolet
    """
    from utils.access_control import is_admin_or_super_admin

    pistolet = get_pistolet_by_id(db, pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut modifier cette donnée
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to modify this pistolet is not authorized for this user"
            )

    # Mettre à jour l'entrée
    updated_pistolet = update_pistolet(db, pistolet_id, **pistolet_data.dict(exclude_unset=True))
    if not updated_pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to update pistolet"
        )

    return PistoletResponse(
        id=str(updated_pistolet.id),
        code=updated_pistolet.code,
        pompe_id=str(updated_pistolet.pompe_id),
        cuve_id=str(updated_pistolet.cuve_id),
        index_initiale=float(updated_pistolet.index_initiale),
        compagnie_id=str(updated_pistolet.compagnie_id),
        statut=updated_pistolet.statut,
        created_at=updated_pistolet.created_at.isoformat()
    )


@router.delete("/pistolets/{pistolet_id}")
@require_permission("pistolets.supprimer")
async def delete_pistolet_endpoint(
    pistolet_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific pistolet
    """
    from utils.access_control import is_admin_or_super_admin

    pistolet = get_pistolet_by_id(db, pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur peut supprimer cette donnée
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to delete this pistolet is not authorized for this user"
            )

    success = delete_pistolet(db, pistolet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to delete pistolet"
        )

    return {"success": True, "message": "Pistolet deleted successfully"}


@router.post("/historique-prix-carburants", response_model=HistoriquePrixCarburantResponse)
@require_permission("historique_prix_carburants.creer")
async def create_historique_prix_carburant_endpoint(
    historique_data: HistoriquePrixCarburantCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new historique prix carburant entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le carburant existe
    from services.structures_service import get_carburant_by_id
    carburant = get_carburant_by_id(db, historique_data.carburant_id)
    if not carburant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carburant not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(carburant.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date d'application
    try:
        date_application = datetime.strptime(historique_data.date_application, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_prix_carburant(
        db,
        carburant_id=historique_data.carburant_id,
        prix_achat=historique_data.prix_achat,
        prix_vente=historique_data.prix_vente,
        date_application=date_application,
        utilisateur_id=utilisateur_id
    )

    return HistoriquePrixCarburantResponse(
        id=str(db_historique.id),
        carburant_id=str(db_historique.carburant_id),
        prix_achat=float(db_historique.prix_achat),
        prix_vente=float(db_historique.prix_vente),
        date_application=db_historique.date_application.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-prix-carburants", response_model=HistoriquePrixCarburantListResponse)
async def get_historique_prix_carburant_list(
    carburant_id: Optional[str] = Query(None, description="Filter by carburant ID"),
    date_application: Optional[str] = Query(None, description="Filter by application date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all historique prix carburant entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "historique_prix_carburants.lire"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'historique_prix_carburants.lire' required"
        )

    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date d'application si fournie
    application_date = None
    if date_application:
        try:
            application_date = datetime.strptime(date_application, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les carburants de la compagnie de l'utilisateur
    from services.structures_service import get_all_carburants
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_carburants = get_all_carburants(db, compagnie_id=user_company_id)
        user_carburant_ids = [str(c.id) for c in user_carburants]
    else:
        # Les admins peuvent voir toutes les données
        all_carburants = get_all_carburants(db)
        user_carburant_ids = [str(c.id) for c in all_carburants]

    # Filtrer les historiques de prix en fonction des carburants autorisés
    historiques_list = get_all_historique_prix_carburant(
        db,
        carburant_id=carburant_id if carburant_id in user_carburant_ids else None,
        date_application=application_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des carburants de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.carburant_id) in user_carburant_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriquePrixCarburantListResponse(
        success=True,
        data=[
            HistoriquePrixCarburantResponse(
                id=str(historique.id),
                carburant_id=str(historique.carburant_id),
                prix_achat=float(historique.prix_achat),
                prix_vente=float(historique.prix_vente),
                date_application=historique.date_application.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-prix-articles", response_model=HistoriquePrixArticleResponse)
@require_permission("historique_prix_articles.creer")
async def create_historique_prix_article_endpoint(
    historique_data: HistoriquePrixArticleCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new historique prix article entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que l'article existe
    from services.structures_service import get_article_by_id
    article = get_article_by_id(db, historique_data.article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(article.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date d'application
    try:
        date_application = datetime.strptime(historique_data.date_application, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_prix_article(
        db,
        article_id=historique_data.article_id,
        prix_achat=historique_data.prix_achat,
        prix_vente=historique_data.prix_vente,
        date_application=date_application,
        utilisateur_id=utilisateur_id
    )

    return HistoriquePrixArticleResponse(
        id=str(db_historique.id),
        article_id=str(db_historique.article_id),
        prix_achat=float(db_historique.prix_achat),
        prix_vente=float(db_historique.prix_vente),
        date_application=db_historique.date_application.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-prix-articles", response_model=HistoriquePrixArticleListResponse)
async def get_historique_prix_article_list(
    article_id: Optional[str] = Query(None, description="Filter by article ID"),
    date_application: Optional[str] = Query(None, description="Filter by application date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all historique prix article entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "historique_prix_articles.lire"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'historique_prix_articles.lire' required"
        )

    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date d'application si fournie
    application_date = None
    if date_application:
        try:
            application_date = datetime.strptime(date_application, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les articles de la compagnie de l'utilisateur
    from services.structures_service import get_all_articles
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_articles = get_all_articles(db, compagnie_id=user_company_id)
        user_article_ids = [str(a.id) for a in user_articles]
    else:
        # Les admins peuvent voir toutes les données
        all_articles = get_all_articles(db)
        user_article_ids = [str(a.id) for a in all_articles]

    # Filtrer les historiques de prix en fonction des articles autorisés
    historiques_list = get_all_historique_prix_article(
        db,
        article_id=article_id if article_id in user_article_ids else None,
        date_application=application_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des articles de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.article_id) in user_article_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriquePrixArticleListResponse(
        success=True,
        data=[
            HistoriquePrixArticleResponse(
                id=str(historique.id),
                article_id=str(historique.article_id),
                prix_achat=float(historique.prix_achat),
                prix_vente=float(historique.prix_vente),
                date_application=historique.date_application.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/historique-index-pistolets", response_model=HistoriqueIndexPistoletResponse)
@prohibit_super_admin_access
async def create_historique_index_pistolet_endpoint(
    historique_data: HistoriqueIndexPistoletCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.creer")),
    db: Session = Depends(get_db)
):
    """
    Create a new historique index pistolet entry
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Vérifier que le pistolet existe
    from services.structures_service import get_pistolet_by_id
    pistolet = get_pistolet_by_id(db, historique_data.pistolet_id)
    if not pistolet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pistolet not found"
        )

    # Vérifier que l'utilisateur est autorisé à accéder à cette compagnie
    if not is_admin_or_super_admin(user_type):
        if str(pistolet.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this company is not authorized for this user"
            )

    # Convertir la date de relevé
    try:
        date_releve = datetime.strptime(historique_data.date_releve, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected format: YYYY-MM-DD"
        )

    utilisateur_id = historique_data.utilisateur_id
    if not utilisateur_id:
        utilisateur_id = str(current_user.id)

    db_historique = create_historique_index_pistolet(
        db,
        pistolet_id=historique_data.pistolet_id,
        index_releve=historique_data.index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=historique_data.observation
    )

    return HistoriqueIndexPistoletResponse(
        id=str(db_historique.id),
        pistolet_id=str(db_historique.pistolet_id),
        index_releve=float(db_historique.index_releve),
        date_releve=db_historique.date_releve.isoformat(),
        utilisateur_id=str(db_historique.utilisateur_id) if db_historique.utilisateur_id else None,
        observation=db_historique.observation,
        created_at=db_historique.created_at.isoformat()
    )


@router.get("/historique-index-pistolets", response_model=HistoriqueIndexPistoletListResponse)
@prohibit_super_admin_access
async def get_historique_index_pistolet_list(
    pistolet_id: Optional[str] = Query(None, description="Filter by pistolet ID"),
    date_releve: Optional[str] = Query(None, description="Filter by relevé date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(create_permission_dependency("historique_index_pistolets.lire")),
    db: Session = Depends(get_db)
):
    """
    Get all historique index pistolet entries with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur

    # Convertir la date de relevé si fournie
    relevé_date = None
    if date_releve:
        try:
            relevé_date = datetime.strptime(date_releve, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Expected format: YYYY-MM-DD"
            )

    # Déterminer la compagnie de l'utilisateur pour les filtres
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Récupérer d'abord tous les pistolets de la compagnie de l'utilisateur
    from services.structures_service import get_all_pistolets
    if not is_admin_or_super_admin(user_type):
        # Les utilisateurs non admin ne peuvent voir que les données de leur compagnie
        user_pistolets = get_all_pistolets(db, compagnie_id=user_company_id)
        user_pistolet_ids = [str(p.id) for p in user_pistolets]
    else:
        # Les admins peuvent voir toutes les données
        all_pistolets = get_all_pistolets(db)
        user_pistolet_ids = [str(p.id) for p in all_pistolets]

    # Filtrer les historiques de relevé en fonction des pistolets autorisés
    historiques_list = get_all_historique_index_pistolet(
        db,
        pistolet_id=pistolet_id if pistolet_id in user_pistolet_ids else None,
        date_releve=relevé_date
    )

    # Filtrer les résultats pour ne contenir que les historiques des pistolets de la bonne compagnie
    if not is_admin_or_super_admin(user_type):
        historiques_list = [
            h for h in historiques_list
            if str(h.pistolet_id) in user_pistolet_ids
        ]

    total = len(historiques_list)

    # Appliquer la pagination
    paginated_historiques = historiques_list[offset:offset+limit]

    return HistoriqueIndexPistoletListResponse(
        success=True,
        data=[
            HistoriqueIndexPistoletResponse(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                created_at=historique.created_at.isoformat()
            )
            for historique in paginated_historiques
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )
# Endpoints pour les clients
@router.post("/clients", response_model=ClientResponse)
@require_permission("clients.creer")
async def create_client_endpoint(
    client_data: ClientCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau client (réservé aux utilisateurs 'administrateur' et 'super_administrateur')
    Seul ce endpoint permet de spécifier explicitement le 'compagnie_id'
    """
    from utils.access_control import is_admin_or_super_admin

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur appartient à la même compagnie que spécifiée
    if not is_admin_or_super_admin(user_type):
        if str(client_data.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to create client for this company is not authorized for this user"
            )

    # Vérifier si un client avec le même code existe déjà
    existing_client = get_client_by_code(db, client_data.code, client_data.compagnie_id)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Client with code {client_data.code} already exists"
        )

    db_client = create_client(
        db,
        code=client_data.code,
        nom=client_data.nom,
        adresse=client_data.adresse,
        telephone=client_data.telephone,
        nif=client_data.nif,
        email=client_data.email,
        compagnie_id=client_data.compagnie_id,
        station_ids=client_data.station_ids,
        type_tiers_id=client_data.type_tiers_id,
        statut=client_data.statut,
        nb_jrs_creance=client_data.nb_jrs_creance,
        devise_facturation=client_data.devise_facturation
    )

    return ClientResponse(
        id=str(db_client.id),
        code=db_client.code,
        nom=db_client.nom,
        adresse=db_client.adresse,
        telephone=db_client.telephone,
        nif=db_client.nif,
        email=db_client.email,
        compagnie_id=str(db_client.compagnie_id),
        station_ids=db_client.station_ids if db_client.station_ids else [],
        type_tiers_id=str(db_client.type_tiers_id) if db_client.type_tiers_id else None,
        statut=db_client.statut,
        nb_jrs_creance=db_client.nb_jrs_creance,
        solde_comptable=float(db_client.solde_comptable) if db_client.solde_comptable else 0.0,
        solde_confirme=float(db_client.solde_confirme) if db_client.solde_confirme else 0.0,
        date_dernier_rapprochement=db_client.date_dernier_rapprochement.isoformat() if db_client.date_dernier_rapprochement else None,
        devise_facturation=db_client.devise_facturation,
        created_at=db_client.created_at.isoformat(),
        updated_at=db_client.updated_at.isoformat() if db_client.updated_at else None
    )


@router.post("/my-clients", response_model=ClientResponse)
async def create_my_client_endpoint(
    client_data: ClientCreateNonAdmin,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau client pour la propre compagnie de l'utilisateur (réservé aux utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie')
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "clients.creer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'clients.creer' required"
        )

    # Ensure that only non-admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to non-admin users"
        )

    # Verify that the user belongs to a company
    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company"
        )

    # Automatically set the company ID to match the user's
    user_compagnie_id = str(current_user.compagnie_id)

    # Vérifier si un client avec le même code existe déjà pour cette compagnie
    existing_client = db.query(Client).filter(
        Client.code == client_data.code,
        Client.compagnie_id == user_compagnie_id
    ).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Client with code {client_data.code} already exists for this company"
        )

    db_client = create_client(
        db,
        code=client_data.code,
        nom=client_data.nom,
        adresse=client_data.adresse,
        telephone=client_data.telephone,
        nif=client_data.nif,
        email=client_data.email,
        compagnie_id=user_compagnie_id,
        station_ids=client_data.station_ids,
        type_tiers_id=client_data.type_tiers_id,
        statut=client_data.statut,
        nb_jrs_creance=client_data.nb_jrs_creance,
        devise_facturation=client_data.devise_facturation
    )

    return ClientResponse(
        id=str(db_client.id),
        code=db_client.code,
        nom=db_client.nom,
        adresse=db_client.adresse,
        telephone=db_client.telephone,
        nif=db_client.nif,
        email=db_client.email,
        compagnie_id=str(db_client.compagnie_id),
        station_ids=db_client.station_ids if db_client.station_ids else [],
        type_tiers_id=str(db_client.type_tiers_id) if db_client.type_tiers_id else None,
        statut=db_client.statut,
        nb_jrs_creance=db_client.nb_jrs_creance,
        solde_comptable=float(db_client.solde_comptable) if db_client.solde_comptable else 0.0,
        solde_confirme=float(db_client.solde_confirme) if db_client.solde_confirme else 0.0,
        date_dernier_rapprochement=db_client.date_dernier_rapprochement.isoformat() if db_client.date_dernier_rapprochement else None,
        devise_facturation=db_client.devise_facturation,
        created_at=db_client.created_at.isoformat(),
        updated_at=db_client.updated_at.isoformat() if db_client.updated_at else None
    )


@router.get("/clients", response_model=ClientListResponse)
@require_permission("clients.lire")
async def get_clients_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les clients avec des filtres optionnels
    Pour les utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie', seuls les clients de leur propre compagnie sont retournés
    Les administrateurs peuvent voir tous les clients s'ils ont la permission
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Déterminer la compagnie en fonction du type d'utilisateur
    if not is_admin_or_super_admin(user_type):
        compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        clients_list = get_all_clients(db, compagnie_id=compagnie_id, statut=statut)
    else:
        # Les admins peuvent voir tous les clients avec filtres optionnels
        clients_list = get_all_clients(db, statut=statut)

    total = len(clients_list)

    # Appliquer la pagination
    paginated_clients = clients_list[offset:offset+limit]

    return ClientListResponse(
        success=True,
        data=[
            ClientResponse(
                id=str(client.id),
                code=client.code,
                nom=client.nom,
                adresse=client.adresse,
                telephone=client.telephone,
                nif=client.nif,
                email=client.email,
                compagnie_id=str(client.compagnie_id),
                station_ids=client.station_ids if client.station_ids else [],
                type_tiers_id=str(client.type_tiers_id) if client.type_tiers_id else None,
                statut=client.statut,
                nb_jrs_creance=client.nb_jrs_creance,
                solde_comptable=float(client.solde_comptable) if client.solde_comptable else 0.0,
                solde_confirme=float(client.solde_confirme) if client.solde_confirme else 0.0,
                date_dernier_rapprochement=client.date_dernier_rapprochement.isoformat() if client.date_dernier_rapprochement else None,
                devise_facturation=client.devise_facturation,
                created_at=client.created_at.isoformat(),
                updated_at=client.updated_at.isoformat() if client.updated_at else None
            )
            for client in paginated_clients
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


# Endpoints pour les fournisseurs
@router.post("/fournisseurs", response_model=FournisseurResponse)
@require_permission("fournisseurs.creer")
async def create_fournisseur_endpoint(
    fournisseur_data: FournisseurCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau fournisseur (réservé aux utilisateurs 'administrateur' et 'super_administrateur')
    Seul ce endpoint permet de spécifier explicitement le 'compagnie_id'
    """
    from utils.access_control import is_admin_or_super_admin

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur appartient à la même compagnie que spécifiée
    if not is_admin_or_super_admin(user_type):
        if str(fournisseur_data.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to create fournisseur for this company is not authorized for this user"
            )

    # Vérifier si un fournisseur avec le même code existe déjà
    existing_fournisseur = get_fournisseur_by_code(db, fournisseur_data.code, fournisseur_data.compagnie_id)
    if existing_fournisseur:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Fournisseur with code {fournisseur_data.code} already exists"
        )

    db_fournisseur = create_fournisseur(
        db,
        code=fournisseur_data.code,
        nom=fournisseur_data.nom,
        adresse=fournisseur_data.adresse,
        telephone=fournisseur_data.telephone,
        nif=fournisseur_data.nif,
        email=fournisseur_data.email,
        compagnie_id=fournisseur_data.compagnie_id,
        station_ids=fournisseur_data.station_ids,
        type_tiers_id=fournisseur_data.type_tiers_id,
        statut=fournisseur_data.statut,
        nb_jrs_creance=fournisseur_data.nb_jrs_creance
    )

    return FournisseurResponse(
        id=str(db_fournisseur.id),
        code=db_fournisseur.code,
        nom=db_fournisseur.nom,
        adresse=db_fournisseur.adresse,
        telephone=db_fournisseur.telephone,
        nif=db_fournisseur.nif,
        email=db_fournisseur.email,
        compagnie_id=str(db_fournisseur.compagnie_id),
        station_ids=db_fournisseur.station_ids if db_fournisseur.station_ids else [],
        type_tiers_id=str(db_fournisseur.type_tiers_id) if db_fournisseur.type_tiers_id else None,
        statut=db_fournisseur.statut,
        nb_jrs_creance=db_fournisseur.nb_jrs_creance,
        solde_comptable=float(db_fournisseur.solde_comptable) if db_fournisseur.solde_comptable else 0.0,
        solde_confirme=float(db_fournisseur.solde_confirme) if db_fournisseur.solde_confirme else 0.0,
        date_dernier_rapprochement=db_fournisseur.date_dernier_rapprochement.isoformat() if db_fournisseur.date_dernier_rapprochement else None,
        created_at=db_fournisseur.created_at.isoformat(),
        updated_at=db_fournisseur.updated_at.isoformat() if db_fournisseur.updated_at else None
    )


@router.post("/my-fournisseurs", response_model=FournisseurResponse)
async def create_my_fournisseur_endpoint(
    fournisseur_data: FournisseurCreateNonAdmin,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau fournisseur pour la propre compagnie de l'utilisateur (réservé aux utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie')
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "fournisseurs.creer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'fournisseurs.creer' required"
        )

    # Ensure that only non-admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to non-admin users"
        )

    # Verify that the user belongs to a company
    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company"
        )

    # Automatically set the company ID to match the user's
    user_compagnie_id = str(current_user.compagnie_id)

    # Vérifier si un fournisseur avec le même code existe déjà pour cette compagnie
    existing_fournisseur = db.query(Fournisseur).filter(
        Fournisseur.code == fournisseur_data.code,
        Fournisseur.compagnie_id == user_compagnie_id
    ).first()
    if existing_fournisseur:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Fournisseur with code {fournisseur_data.code} already exists for this company"
        )

    db_fournisseur = create_fournisseur(
        db,
        code=fournisseur_data.code,
        nom=fournisseur_data.nom,
        adresse=fournisseur_data.adresse,
        telephone=fournisseur_data.telephone,
        nif=fournisseur_data.nif,
        email=fournisseur_data.email,
        compagnie_id=user_compagnie_id,
        station_ids=fournisseur_data.station_ids,
        type_tiers_id=fournisseur_data.type_tiers_id,
        statut=fournisseur_data.statut,
        nb_jrs_creance=fournisseur_data.nb_jrs_creance
    )

    return FournisseurResponse(
        id=str(db_fournisseur.id),
        code=db_fournisseur.code,
        nom=db_fournisseur.nom,
        adresse=db_fournisseur.adresse,
        telephone=db_fournisseur.telephone,
        nif=db_fournisseur.nif,
        email=db_fournisseur.email,
        compagnie_id=str(db_fournisseur.compagnie_id),
        station_ids=db_fournisseur.station_ids if db_fournisseur.station_ids else [],
        type_tiers_id=str(db_fournisseur.type_tiers_id) if db_fournisseur.type_tiers_id else None,
        statut=db_fournisseur.statut,
        nb_jrs_creance=db_fournisseur.nb_jrs_creance,
        solde_comptable=float(db_fournisseur.solde_comptable) if db_fournisseur.solde_comptable else 0.0,
        solde_confirme=float(db_fournisseur.solde_confirme) if db_fournisseur.solde_confirme else 0.0,
        date_dernier_rapprochement=db_fournisseur.date_dernier_rapprochement.isoformat() if db_fournisseur.date_dernier_rapprochement else None,
        created_at=db_fournisseur.created_at.isoformat(),
        updated_at=db_fournisseur.updated_at.isoformat() if db_fournisseur.updated_at else None
    )


@router.get("/fournisseurs", response_model=FournisseurListResponse)
@require_permission("fournisseurs.lire")
async def get_fournisseurs_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les fournisseurs avec des filtres optionnels
    Pour les utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie', seuls les fournisseurs de leur propre compagnie sont retournés
    Les administrateurs peuvent voir tous les fournisseurs s'ils ont la permission
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Déterminer la compagnie en fonction du type d'utilisateur
    if not is_admin_or_super_admin(user_type):
        compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        fournisseurs_list = get_all_fournisseurs(db, compagnie_id=compagnie_id, statut=statut)
    else:
        # Les admins peuvent voir tous les fournisseurs avec filtres optionnels
        fournisseurs_list = get_all_fournisseurs(db, statut=statut)

    total = len(fournisseurs_list)

    # Appliquer la pagination
    paginated_fournisseurs = fournisseurs_list[offset:offset+limit]

    return FournisseurListResponse(
        success=True,
        data=[
            FournisseurResponse(
                id=str(fournisseur.id),
                code=fournisseur.code,
                nom=fournisseur.nom,
                adresse=fournisseur.adresse,
                telephone=fournisseur.telephone,
                nif=fournisseur.nif,
                email=fournisseur.email,
                compagnie_id=str(fournisseur.compagnie_id),
                station_ids=fournisseur.station_ids if fournisseur.station_ids else [],
                type_tiers_id=str(fournisseur.type_tiers_id) if fournisseur.type_tiers_id else None,
                statut=fournisseur.statut,
                nb_jrs_creance=fournisseur.nb_jrs_creance,
                solde_comptable=float(fournisseur.solde_comptable) if fournisseur.solde_comptable else 0.0,
                solde_confirme=float(fournisseur.solde_confirme) if fournisseur.solde_confirme else 0.0,
                date_dernier_rapprochement=fournisseur.date_dernier_rapprochement.isoformat() if fournisseur.date_dernier_rapprochement else None,
                created_at=fournisseur.created_at.isoformat(),
                updated_at=fournisseur.updated_at.isoformat() if fournisseur.updated_at else None
            )
            for fournisseur in paginated_fournisseurs
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


# Endpoints pour les employés
@router.post("/employes", response_model=EmployeResponse)
@require_permission("employes.creer")
async def create_employe_endpoint(
    employe_data: EmployeCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel employé (réservé aux utilisateurs 'administrateur' et 'super_administrateur')
    Seul ce endpoint permet de spécifier explicitement le 'compagnie_id'
    """
    from utils.access_control import is_admin_or_super_admin

    user_type = current_user.type_utilisateur
    # Vérifier que l'utilisateur appartient à la même compagnie que spécifiée
    if not is_admin_or_super_admin(user_type):
        if str(employe_data.compagnie_id) != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to create employe for this company is not authorized for this user"
            )

    # Vérifier si un employé avec le même code existe déjà
    existing_employe = get_employe_by_code(db, employe_data.code, employe_data.compagnie_id)
    if existing_employe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employe with code {employe_data.code} already exists"
        )

    db_employe = create_employe(
        db,
        code=employe_data.code,
        nom=employe_data.nom,
        prenom=employe_data.prenom,
        adresse=employe_data.adresse,
        telephone=employe_data.telephone,
        poste=employe_data.poste,
        salaire_base=employe_data.salaire_base,
        avances=employe_data.avances,
        creances=employe_data.creances,
        station_ids=employe_data.station_ids,
        compagnie_id=employe_data.compagnie_id,
        statut=employe_data.statut
    )

    return EmployeResponse(
        id=str(db_employe.id),
        code=db_employe.code,
        nom=db_employe.nom,
        prenom=db_employe.prenom,
        adresse=db_employe.adresse,
        telephone=db_employe.telephone,
        poste=db_employe.poste,
        salaire_base=float(db_employe.salaire_base),
        avances=float(db_employe.avances),
        creances=float(db_employe.creances),
        compagnie_id=str(db_employe.compagnie_id),
        station_ids=db_employe.station_ids if db_employe.station_ids else [],
        statut=db_employe.statut,
        created_at=db_employe.created_at.isoformat(),
        updated_at=db_employe.updated_at.isoformat() if db_employe.updated_at else None
    )


@router.post("/my-employes", response_model=EmployeResponse)
async def create_my_employe_endpoint(
    employe_data: EmployeCreateNonAdmin,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel employé pour la propre compagnie de l'utilisateur (réservé aux utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie')
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "employes.creer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'employes.creer' required"
        )

    # Ensure that only non-admin users can access this endpoint
    user_type = current_user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to non-admin users"
        )

    # Verify that the user belongs to a company
    if not current_user.compagnie_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company"
        )

    # Automatically set the company ID to match the user's
    user_compagnie_id = str(current_user.compagnie_id)

    # Vérifier si un employé avec le même code existe déjà pour cette compagnie
    existing_employe = db.query(Employe).filter(
        Employe.code == employe_data.code,
        Employe.compagnie_id == user_compagnie_id
    ).first()
    if existing_employe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employe with code {employe_data.code} already exists for this company"
        )

    db_employe = create_employe(
        db,
        code=employe_data.code,
        nom=employe_data.nom,
        prenom=employe_data.prenom,
        adresse=employe_data.adresse,
        telephone=employe_data.telephone,
        poste=employe_data.poste,
        salaire_base=employe_data.salaire_base,
        avances=employe_data.avances,
        creances=employe_data.creances,
        station_ids=employe_data.station_ids,
        compagnie_id=user_compagnie_id,
        statut=employe_data.statut
    )

    return EmployeResponse(
        id=str(db_employe.id),
        code=db_employe.code,
        nom=db_employe.nom,
        prenom=db_employe.prenom,
        adresse=db_employe.adresse,
        telephone=db_employe.telephone,
        poste=db_employe.poste,
        salaire_base=float(db_employe.salaire_base),
        avances=float(db_employe.avances),
        creances=float(db_employe.creances),
        compagnie_id=str(db_employe.compagnie_id),
        station_ids=db_employe.station_ids if db_employe.station_ids else [],
        statut=db_employe.statut,
        created_at=db_employe.created_at.isoformat(),
        updated_at=db_employe.updated_at.isoformat() if db_employe.updated_at else None
    )


@router.get("/employes", response_model=EmployeListResponse)
@require_permission("employes.lire")
async def get_employes_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les employés avec des filtres optionnels
    Pour les utilisateurs 'gérant_compagnie' et 'utilisateur_compagnie', seuls les employés de leur propre compagnie sont retournés
    Les administrateurs peuvent voir tous les employés s'ils ont la permission
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Déterminer la compagnie en fonction du type d'utilisateur
    if not is_admin_or_super_admin(user_type):
        compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        employes_list = get_all_employes(db, compagnie_id=compagnie_id, statut=statut)
    else:
        # Les admins peuvent voir tous les employés avec filtres optionnels
        employes_list = get_all_employes(db, statut=statut)

    total = len(employes_list)

    # Appliquer la pagination
    paginated_employes = employes_list[offset:offset+limit]

    return EmployeListResponse(
        success=True,
        data=[
            EmployeResponse(
                id=str(employe.id),
                code=employe.code,
                nom=employe.nom,
                prenom=employe.prenom,
                adresse=employe.adresse,
                telephone=employe.telephone,
                poste=employe.poste,
                salaire_base=float(employe.salaire_base),
                avances=float(employe.avances),
                creances=float(employe.creances),
                compagnie_id=str(employe.compagnie_id),
                station_ids=employe.station_ids if employe.station_ids else [],
                statut=employe.statut,
                created_at=employe.created_at.isoformat(),
                updated_at=employe.updated_at.isoformat() if employe.updated_at else None
            )
            for employe in paginated_employes
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )
# Endpoints pour les types de tiers
@router.post("/type-tiers", response_model=TypeTiersResponse)
@require_permission("type_tiers.creer")
async def create_type_tiers_endpoint(
    type_tiers_data: TypeTiersCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau type de tiers (réservé aux administrateurs)
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Seuls les administrateurs peuvent créer des types de tiers
    if not is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent créer des types de tiers"
        )

    # Vérifier si un type de tiers avec le même libellé existe déjà
    existing_type = db.query(TypeTiers).filter(
        TypeTiers.libelle == type_tiers_data.libelle
    ).first()
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Type de tiers avec le libellé '{type_tiers_data.libelle}' existe déjà"
        )

    db_type_tiers = create_type_tiers(
        db,
        type=type_tiers_data.type,
        libelle=type_tiers_data.libelle,
        num_compte=type_tiers_data.num_compte
    )

    return TypeTiersResponse(
        id=str(db_type_tiers.id),
        type=db_type_tiers.type,
        libelle=db_type_tiers.libelle,
        num_compte=db_type_tiers.num_compte,
        created_at=db_type_tiers.created_at.isoformat(),
        updated_at=db_type_tiers.updated_at.isoformat() if db_type_tiers.updated_at else None
    )


@router.get("/type-tiers", response_model=TypeTiersListResponse)
async def get_types_tiers_list(
    type_filter: Optional[str] = Query(None, description="Filter by type (client, fournisseur, employe)"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les types de tiers avec des filtres optionnels
    Accès autorisé à tous les utilisateurs pour la consultation
    """
    # Récupérer tous les types de tiers ou filtrer par type
    types_tiers_list = get_type_tiers_by_type(db, type_filter=type_filter)

    total = len(types_tiers_list)

    # Appliquer la pagination
    paginated_types = types_tiers_list[offset:offset+limit]

    return TypeTiersListResponse(
        success=True,
        data=[
            TypeTiersResponse(
                id=str(type_tiers.id),
                type=type_tiers.type,
                libelle=type_tiers.libelle,
                num_compte=type_tiers.num_compte,
                created_at=type_tiers.created_at.isoformat(),
                updated_at=type_tiers.updated_at.isoformat() if type_tiers.updated_at else None
            )
            for type_tiers in paginated_types
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )
