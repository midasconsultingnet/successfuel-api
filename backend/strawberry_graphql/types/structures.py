import strawberry
from typing import List, Optional
from datetime import datetime
from models.structures import (
    Pays as PaysModel,
    Compagnie as CompagnieModel,
    Module as ModuleModel,
    Permission as PermissionModel,
    Profil as ProfilModel,
    ProfilPermission as ProfilPermissionModel,
    Station as StationModel,
    Utilisateur as UtilisateurModel,
    FamilleArticle as FamilleArticleModel,
    TypeTiers as TypeTiersModel,
    Article as ArticleModel,
    Carburant as CarburantModel,
    Cuve as CuveModel,
    Pompe as PompeModel,
    Pistolet as PistoletModel,
)
from models.comptabilite import (
    PlanComptable as PlanComptableModel,
)

from models.structures import (
    Client as ClientModel,
    Fournisseur as FournisseurModel,
    Employe as EmployeModel,
    MethodePaiement as MethodePaiementModel,
    Tresorerie as TresorerieModel,
    BarremageCuve as BarremageCuveModel,
    HistoriquePrixCarburant as HistoriquePrixCarburantModel,
    HistoriquePrixArticle as HistoriquePrixArticleModel,
    HistoriqueIndexPistolet as HistoriqueIndexPistoletModel
)
from .base import BaseGraphQLType

@strawberry.type
class Pays(BaseGraphQLType):
    code_pays: str
    nom_pays: str
    devise_principale: str
    taux_tva_par_defaut: Optional[float] = 0
    systeme_comptable: Optional[str] = 'OHADA'
    date_application_tva: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: PaysModel):
        return cls(
            id=str(instance.id),
            code_pays=instance.code_pays,
            nom_pays=instance.nom_pays,
            devise_principale=instance.devise_principale,
            taux_tva_par_defaut=float(instance.taux_tva_par_defaut) if instance.taux_tva_par_defaut else 0,
            systeme_comptable=instance.systeme_comptable,
            date_application_tva=instance.date_application_tva.isoformat() if instance.date_application_tva else None,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Compagnie(BaseGraphQLType):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    pays_id: str
    devise_principale: str = 'MGA'

    @classmethod
    def from_instance(cls, instance: CompagnieModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            nom=instance.nom,
            adresse=instance.adresse,
            telephone=instance.telephone,
            email=instance.email,
            nif=instance.nif,
            statut=instance.statut,
            pays_id=str(instance.pays_id),
            devise_principale=instance.devise_principale,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Module(BaseGraphQLType):
    libelle: str

    @classmethod
    def from_instance(cls, instance: ModuleModel):
        return cls(
            id=str(instance.id),
            libelle=instance.libelle,
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class Permission:
    id: str
    libelle: str
    description: Optional[str] = None
    module_id: Optional[str] = None
    statut: str = 'Actif'
    created_at: datetime

    @classmethod
    def from_instance(cls, instance: PermissionModel):
        return cls(
            id=str(instance.id),
            libelle=instance.libelle,
            description=instance.description,
            module_id=str(instance.module_id) if instance.module_id else None,
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class Profil(BaseGraphQLType):
    code: str
    libelle: str
    compagnie_id: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: ProfilModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            libelle=instance.libelle,
            compagnie_id=str(instance.compagnie_id) if instance.compagnie_id else None,
            description=instance.description,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class ProfilPermission:
    id: str
    profil_id: str
    permission_id: str

    @classmethod
    def from_instance(cls, instance: ProfilPermissionModel):
        return cls(
            id=str(instance.id),
            profil_id=str(instance.profil_id),
            permission_id=str(instance.permission_id),
        )

@strawberry.type
class Station(BaseGraphQLType):
    compagnie_id: str
    code: str
    nom: str
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    pays_id: str

    @classmethod
    def from_instance(cls, instance: StationModel):
        return cls(
            id=str(instance.id),
            compagnie_id=str(instance.compagnie_id),
            code=instance.code,
            nom=instance.nom,
            telephone=instance.telephone,
            email=instance.email,
            adresse=instance.adresse,
            pays_id=str(instance.pays_id),
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class Utilisateur(BaseGraphQLType):
    login: str
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    profil_id: Optional[str] = None
    stations_user: Optional[List[str]] = None
    last_login: Optional[datetime] = None
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: UtilisateurModel):
        return cls(
            id=str(instance.id),
            login=instance.login,
            nom=instance.nom,
            profil_id=str(instance.profil_id) if instance.profil_id else None,
            email=instance.email,
            telephone=instance.telephone,
            stations_user=instance.stations_user if instance.stations_user else [],
            statut=instance.statut,
            last_login=instance.last_login,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class FamilleArticle(BaseGraphQLType):
    code: str
    libelle: str
    compagnie_id: str
    parent_id: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: FamilleArticleModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            libelle=instance.libelle,
            compagnie_id=str(instance.compagnie_id),
            statut=instance.statut,
            parent_id=str(instance.parent_id) if instance.parent_id else None,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class PlanComptable(BaseGraphQLType):
    numero: str
    intitule: str
    classe: str
    type_compte: str
    sens_solde: Optional[str] = None
    compte_parent_id: Optional[str] = None
    description: Optional[str] = None
    est_compte_racine: bool = False
    est_compte_de_resultat: bool = False
    est_compte_actif: bool = True
    pays_id: Optional[str] = None
    est_specifique_pays: bool = False
    code_pays: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: PlanComptableModel):
        return cls(
            id=str(instance.id),
            numero=instance.numero,
            intitule=instance.intitule,
            classe=instance.classe,
            type_compte=instance.type_compte,
            sens_solde=instance.sens_solde,
            compte_parent_id=str(instance.compte_parent_id) if instance.compte_parent_id else None,
            description=instance.description,
            statut=instance.statut,
            est_compte_racine=instance.est_compte_racine,
            est_compte_de_resultat=instance.est_compte_de_resultat,
            est_compte_actif=instance.est_compte_actif,
            pays_id=str(instance.pays_id) if instance.pays_id else None,
            est_specifique_pays=instance.est_specifique_pays,
            code_pays=instance.code_pays,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class TypeTiers:
    id: str
    type: str
    libelle: str
    num_compte: Optional[str] = None
    compagnie_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_instance(cls, instance: TypeTiersModel):
        return cls(
            id=str(instance.id),
            type=instance.type,
            libelle=instance.libelle,
            num_compte=instance.num_compte,
            compagnie_id=str(instance.compagnie_id),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Article(BaseGraphQLType):
    code: str
    libelle: str
    codebarre: Optional[str] = None
    famille_id: Optional[str] = None
    unite: str = 'Litre'
    compagnie_id: str
    type_article: str = 'produit'
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    tva: float = 0.0
    taxes_applicables: Optional[List[str]] = None
    stock_minimal: float = 0.0

    @classmethod
    def from_instance(cls, instance: ArticleModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            libelle=instance.libelle,
            codebarre=instance.codebarre,
            famille_id=str(instance.famille_id) if instance.famille_id else None,
            unite=instance.unite,
            compagnie_id=str(instance.compagnie_id),
            type_article=instance.type_article,
            prix_achat=float(instance.prix_achat) if instance.prix_achat else 0.0,
            prix_vente=float(instance.prix_vente) if instance.prix_vente else 0.0,
            tva=float(instance.tva) if instance.tva else 0.0,
            taxes_applicables=instance.taxes_applicables if instance.taxes_applicables else [],
            stock_minimal=float(instance.stock_minimal) if instance.stock_minimal else 0.0,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Carburant(BaseGraphQLType):
    code: str
    libelle: str
    type: str
    compagnie_id: str
    prix_achat: float = 0.0
    prix_vente: float = 0.0

    @classmethod
    def from_instance(cls, instance: CarburantModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            libelle=instance.libelle,
            type=instance.type,
            compagnie_id=str(instance.compagnie_id),
            prix_achat=float(instance.prix_achat) if instance.prix_achat else 0.0,
            prix_vente=float(instance.prix_vente) if instance.prix_vente else 0.0,
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Cuve(BaseGraphQLType):
    station_id: str
    code: str
    capacite: float
    carburant_id: Optional[str] = None
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: CuveModel):
        return cls(
            id=str(instance.id),
            station_id=str(instance.station_id),
            code=instance.code,
            capacite=float(instance.capacite),
            carburant_id=str(instance.carburant_id) if instance.carburant_id else None,
            compagnie_id=str(instance.compagnie_id),
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Pompe(BaseGraphQLType):
    station_id: str
    code: str
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: PompeModel):
        return cls(
            id=str(instance.id),
            station_id=str(instance.station_id),
            code=instance.code,
            compagnie_id=str(instance.compagnie_id),
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class Pistolet(BaseGraphQLType):
    code: str
    pompe_id: str
    cuve_id: str
    index_initiale: float = 0.0
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: PistoletModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            pompe_id=str(instance.pompe_id),
            cuve_id=str(instance.cuve_id),
            index_initiale=float(instance.index_initiale) if instance.index_initiale else 0.0,
            compagnie_id=str(instance.compagnie_id),
            statut=instance.statut,
            created_at=instance.created_at,
        )

@strawberry.type
class Client(BaseGraphQLType):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    compagnie_id: str
    station_ids: Optional[List[str]] = None
    type_tiers_id: Optional[str] = None
    nb_jrs_creance: int = 0
    solde_comptable: float = 0.0
    solde_confirme: float = 0.0
    date_dernier_rapprochement: Optional[datetime] = None
    devise_facturation: str = 'MGA'

    @classmethod
    def from_instance(cls, instance: ClientModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            nom=instance.nom,
            adresse=instance.adresse,
            telephone=instance.telephone,
            nif=instance.nif,
            email=instance.email,
            compagnie_id=str(instance.compagnie_id),
            station_ids=instance.station_ids if instance.station_ids else [],
            type_tiers_id=str(instance.type_tiers_id) if instance.type_tiers_id else None,
            statut=instance.statut,
            nb_jrs_creance=instance.nb_jrs_creance,
            solde_comptable=float(instance.solde_comptable) if instance.solde_comptable else 0.0,
            solde_confirme=float(instance.solde_confirme) if instance.solde_confirme else 0.0,
            date_dernier_rapprochement=instance.date_dernier_rapprochement,
            devise_facturation=instance.devise_facturation,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Fournisseur(BaseGraphQLType):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    nif: Optional[str] = None
    email: Optional[str] = None
    compagnie_id: str
    station_ids: Optional[List[str]] = None
    type_tiers_id: Optional[str] = None
    nb_jrs_creance: int = 0
    solde_comptable: float = 0.0
    solde_confirme: float = 0.0
    date_dernier_rapprochement: Optional[datetime] = None

    @classmethod
    def from_instance(cls, instance: FournisseurModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            nom=instance.nom,
            adresse=instance.adresse,
            telephone=instance.telephone,
            nif=instance.nif,
            email=instance.email,
            compagnie_id=str(instance.compagnie_id),
            station_ids=instance.station_ids if instance.station_ids else [],
            type_tiers_id=str(instance.type_tiers_id) if instance.type_tiers_id else None,
            statut=instance.statut,
            nb_jrs_creance=instance.nb_jrs_creance,
            solde_comptable=float(instance.solde_comptable) if instance.solde_comptable else 0.0,
            solde_confirme=float(instance.solde_confirme) if instance.solde_confirme else 0.0,
            date_dernier_rapprochement=instance.date_dernier_rapprochement,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Employe(BaseGraphQLType):
    code: str
    nom: str
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    poste: Optional[str] = None
    salaire_base: float = 0.0
    station_ids: Optional[List[str]] = None
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: EmployeModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            nom=instance.nom,
            prenom=instance.prenom,
            adresse=instance.adresse,
            telephone=instance.telephone,
            poste=instance.poste,
            salaire_base=float(instance.salaire_base) if instance.salaire_base else 0.0,
            station_ids=instance.station_ids if instance.station_ids else [],
            compagnie_id=str(instance.compagnie_id),
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class MethodePaiement:
    id: str
    type_tresorerie: str
    mode_paiement: Optional[List[str]] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_instance(cls, instance: MethodePaiementModel):
        return cls(
            id=str(instance.id),
            type_tresorerie=instance.type_tresorerie,
            mode_paiement=instance.mode_paiement if instance.mode_paiement else [],
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class Tresorerie(BaseGraphQLType):
    code: str
    libelle: str
    compagnie_id: str
    station_ids: Optional[List[str]] = None
    solde: float = 0.0
    devise_code: str = 'MGA'
    taux_change: float = 1.0
    fournisseur_id: Optional[str] = None
    type_tresorerie: Optional[str] = None
    methode_paiement: Optional[List[str]] = None
    solde_theorique: float = 0.0
    solde_reel: float = 0.0
    date_dernier_rapprochement: Optional[datetime] = None
    utilisateur_dernier_rapprochement: Optional[str] = None
    type_tresorerie_libelle: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: TresorerieModel):
        return cls(
            id=str(instance.id),
            code=instance.code,
            libelle=instance.libelle,
            compagnie_id=str(instance.compagnie_id),
            station_ids=instance.station_ids if instance.station_ids else [],
            solde=float(instance.solde) if instance.solde else 0.0,
            devise_code=instance.devise_code,
            taux_change=float(instance.taux_change) if instance.taux_change else 1.0,
            fournisseur_id=str(instance.fournisseur_id) if instance.fournisseur_id else None,
            type_tresorerie=str(instance.type_tresorerie) if instance.type_tresorerie else None,
            methode_paiement=instance.methode_paiement if instance.methode_paiement else [],
            statut=instance.statut,
            solde_theorique=float(instance.solde_theorique) if instance.solde_theorique else 0.0,
            solde_reel=float(instance.solde_reel) if instance.solde_reel else 0.0,
            date_dernier_rapprochement=instance.date_dernier_rapprochement,
            utilisateur_dernier_rapprochement=str(instance.utilisateur_dernier_rapprochement) if instance.utilisateur_dernier_rapprochement else None,
            type_tresorerie_libelle=instance.type_tresorerie_libelle,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class BarremageCuve(BaseGraphQLType):
    cuve_id: str
    station_id: str
    hauteur: float
    volume: float
    compagnie_id: str

    @classmethod
    def from_instance(cls, instance: BarremageCuveModel):
        return cls(
            id=str(instance.id),
            cuve_id=str(instance.cuve_id),
            station_id=str(instance.station_id),
            hauteur=float(instance.hauteur) if instance.hauteur else 0.0,
            volume=float(instance.volume) if instance.volume else 0.0,
            compagnie_id=str(instance.compagnie_id),
            statut=instance.statut,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

@strawberry.type
class HistoriquePrixCarburant(BaseGraphQLType):
    carburant_id: str
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    date_application: str
    utilisateur_id: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: HistoriquePrixCarburantModel):
        return cls(
            id=str(instance.id),
            carburant_id=str(instance.carburant_id),
            prix_achat=float(instance.prix_achat) if instance.prix_achat else 0.0,
            prix_vente=float(instance.prix_vente) if instance.prix_vente else 0.0,
            date_application=instance.date_application.isoformat() if instance.date_application else None,
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            created_at=instance.created_at,
        )

@strawberry.type
class HistoriquePrixArticle(BaseGraphQLType):
    article_id: str
    prix_achat: float = 0.0
    prix_vente: float = 0.0
    date_application: str
    utilisateur_id: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: HistoriquePrixArticleModel):
        return cls(
            id=str(instance.id),
            article_id=str(instance.article_id),
            prix_achat=float(instance.prix_achat) if instance.prix_achat else 0.0,
            prix_vente=float(instance.prix_vente) if instance.prix_vente else 0.0,
            date_application=instance.date_application.isoformat() if instance.date_application else None,
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            created_at=instance.created_at,
        )

@strawberry.type
class HistoriqueIndexPistolet(BaseGraphQLType):
    pistolet_id: str
    index_releve: float
    date_releve: str
    utilisateur_id: Optional[str] = None
    observation: Optional[str] = None

    @classmethod
    def from_instance(cls, instance: HistoriqueIndexPistoletModel):
        return cls(
            id=str(instance.id),
            pistolet_id=str(instance.pistolet_id),
            index_releve=float(instance.index_releve) if instance.index_releve else 0.0,
            date_releve=instance.date_releve.isoformat() if instance.date_releve else None,
            utilisateur_id=str(instance.utilisateur_id) if instance.utilisateur_id else None,
            observation=instance.observation,
            statut=instance.statut,
            created_at=instance.created_at,
        )