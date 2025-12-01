from typing import List, Optional
from strawberry import field, type
import strawberry
from datetime import date
from ..context import CustomContext
from ...models.structures import (
    Cuve, Carburant, Pompe, Pistolet, FamilleArticle, Article, 
    Fournisseur, Client, Employe, Tresorerie, BarremageCuve, 
    HistoriquePrixCarburant, HistoriquePrixArticle, HistoriqueIndexPistolet
)
from ...models.auth import Utilisateur, Profil
from ...utils.graphql_permissions import IsAuthenticated
from ...utils.graphql_utils import get_current_user_company_id


# Types GraphQL pour les entités de gestion des structures
@strawberry.type
class CuveType:
    id: str
    station_id: str
    code: str
    capacite: float
    carburant_id: Optional[str]
    compagnie_id: str
    temperature: Optional[float]
    statut: str
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class CarburantType:
    id: str
    code: str
    libelle: str
    type: str
    compagnie_id: str
    prix_achat: Optional[float]
    prix_vente: Optional[float]
    qualite: Optional[float]
    statut: str
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class PompeType:
    id: str
    station_id: str
    code: str
    compagnie_id: str
    statut: str
    created_at: str


@strawberry.type
class PistoletType:
    id: str
    code: str
    pompe_id: Optional[str]
    cuve_id: Optional[str]
    index_initiale: Optional[float]
    compagnie_id: str
    statut: str
    created_at: str


@strawberry.type
class BarremageCuveType:
    id: str
    cuve_id: str
    station_id: str
    hauteur: float
    volume: float
    statut: str
    created_at: str
    updated_at: Optional[str]
    compagnie_id: str


@strawberry.type
class HistoriquePrixCarburantType:
    id: str
    carburant_id: str
    prix_achat: Optional[float]
    prix_vente: Optional[float]
    date_application: str
    utilisateur_id: Optional[str]
    created_at: str


@strawberry.type
class HistoriquePrixArticleType:
    id: str
    article_id: str
    prix_achat: Optional[float]
    prix_vente: Optional[float]
    date_application: str
    utilisateur_id: Optional[str]
    created_at: str


@strawberry.type
class HistoriqueIndexPistoletType:
    id: str
    pistolet_id: str
    index_releve: float
    date_releve: str
    utilisateur_id: Optional[str]
    observation: Optional[str]
    statut: str
    created_at: str


@strawberry.type
class FamilleArticleType:
    id: str
    code: str
    libelle: str
    compagnie_id: str
    statut: str
    parent_id: Optional[str]
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class ArticleType:
    id: str
    code: str
    libelle: str
    codebarre: Optional[str]
    famille_id: Optional[str]
    unite: str
    unite_principale: Optional[str]
    unite_stock: Optional[str]
    compagnie_id: str
    type_article: str
    prix_achat: Optional[float]
    prix_vente: Optional[float]
    tva: Optional[float]
    taxes_applicables: Optional[str]  # JSON
    stock_minimal: Optional[float]
    statut: str
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class FournisseurType:
    id: str
    code: str
    nom: str
    adresse: Optional[str]
    telephone: Optional[str]
    nif: Optional[str]
    email: Optional[str]
    compagnie_id: str
    station_ids: Optional[str]  # JSON
    type_tiers_id: Optional[str]
    statut: str
    nb_jrs_creance: Optional[int]
    solde_comptable: Optional[float]
    solde_confirme: Optional[float]
    date_dernier_rapprochement: Optional[str]
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class ClientType:
    id: str
    code: str
    nom: str
    adresse: Optional[str]
    telephone: Optional[str]
    nif: Optional[str]
    email: Optional[str]
    compagnie_id: str
    station_ids: Optional[str]  # JSON
    type_tiers_id: Optional[str]
    statut: str
    nb_jrs_creance: Optional[int]
    solde_comptable: Optional[float]
    solde_confirme: Optional[float]
    date_dernier_rapprochement: Optional[str]
    devise_facturation: str
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class EmployeType:
    id: str
    code: str
    nom: str
    prenom: Optional[str]
    adresse: Optional[str]
    telephone: Optional[str]
    poste: Optional[str]
    salaire_base: Optional[float]
    avances: Optional[float]
    creances: Optional[float]
    station_ids: Optional[str]  # JSON
    compagnie_id: str
    statut: str
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class TresorerieType:
    id: str
    code: str
    libelle: str
    compagnie_id: str
    station_ids: Optional[str]  # JSON
    solde: Optional[float]
    devise_code: str
    taux_change: Optional[float]
    fournisseur_id: Optional[str]
    type_tresorerie: Optional[str]
    methode_paiement: Optional[str]  # JSON
    statut: str
    solde_theorique: Optional[float]
    solde_reel: Optional[float]
    date_dernier_rapprochement: Optional[str]
    utilisateur_dernier_rapprochement: Optional[str]
    type_tresorerie_libelle: Optional[str]
    created_at: str
    updated_at: Optional[str]


# Résolveurs pour la gestion des structures
@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def cuves(self, info: strawberry.Info) -> List[CuveType]:
        """Récupère toutes les cuves accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        # Vérifier si l'utilisateur est admin ou super_admin pour accéder à toutes les données
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Cuve)
        
        if not is_admin:
            query = query.filter(Cuve.compagnie_id == user_company_id)
        
        cuves = query.all()
        return [
            CuveType(
                id=str(cuve.id),
                station_id=str(cuve.station_id),
                code=cuve.code,
                capacite=float(cuve.capacite or 0),
                carburant_id=str(cuve.carburant_id) if cuve.carburant_id else None,
                compagnie_id=str(cuve.compagnie_id),
                temperature=float(cuve.temperature or 0) if cuve.temperature else None,
                statut=cuve.statut,
                created_at=cuve.created_at.isoformat(),
                updated_at=cuve.updated_at.isoformat() if cuve.updated_at else None
            )
            for cuve in cuves
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def carburants(self, info: strawberry.Info) -> List[CarburantType]:
        """Récupère tous les carburants accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Carburant)
        
        if not is_admin:
            query = query.filter(Carburant.compagnie_id == user_company_id)
        
        carburants = query.all()
        return [
            CarburantType(
                id=str(carburant.id),
                code=carburant.code,
                libelle=carburant.libelle,
                type=carburant.type,
                compagnie_id=str(carburant.compagnie_id),
                prix_achat=float(carburant.prix_achat or 0) if carburant.prix_achat else None,
                prix_vente=float(carburant.prix_vente or 0) if carburant.prix_vente else None,
                qualite=float(carburant.qualite or 0) if carburant.qualite else None,
                statut=carburant.statut,
                created_at=carburant.created_at.isoformat(),
                updated_at=carburant.updated_at.isoformat() if carburant.updated_at else None
            )
            for carburant in carburants
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def pompes(self, info: strawberry.Info) -> List[PompeType]:
        """Récupère toutes les pompes accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Pompe)
        
        if not is_admin:
            query = query.filter(Pompe.compagnie_id == user_company_id)
        
        pompes = query.all()
        return [
            PompeType(
                id=str(pompe.id),
                station_id=str(pompe.station_id),
                code=pompe.code,
                compagnie_id=str(pompe.compagnie_id),
                statut=pompe.statut,
                created_at=pompe.created_at.isoformat()
            )
            for pompe in pompes
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def pistolets(self, info: strawberry.Info) -> List[PistoletType]:
        """Récupère tous les pistolets accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Pistolet)
        
        if not is_admin:
            query = query.filter(Pistolet.compagnie_id == user_company_id)
        
        pistolets = query.all()
        return [
            PistoletType(
                id=str(pistolet.id),
                code=pistolet.code,
                pompe_id=str(pistolet.pompe_id) if pistolet.pompe_id else None,
                cuve_id=str(pistolet.cuve_id) if pistolet.cuve_id else None,
                index_initiale=float(pistolet.index_initiale or 0) if pistolet.index_initiale else None,
                compagnie_id=str(pistolet.compagnie_id),
                statut=pistolet.statut,
                created_at=pistolet.created_at.isoformat()
            )
            for pistolet in pistolets
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def barremage_cuves(self, info: strawberry.Info) -> List[BarremageCuveType]:
        """Récupère tous les barèmes de jauge accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(BarremageCuve)
        
        if not is_admin:
            query = query.filter(BarremageCuve.compagnie_id == user_company_id)
        
        barremages = query.all()
        return [
            BarremageCuveType(
                id=str(barremage.id),
                cuve_id=str(barremage.cuve_id),
                station_id=str(barremage.station_id),
                hauteur=float(barremage.hauteur or 0),
                volume=float(barremage.volume or 0),
                statut=barremage.statut,
                created_at=barremage.created_at.isoformat(),
                updated_at=barremage.updated_at.isoformat() if barremage.updated_at else None,
                compagnie_id=str(barremage.compagnie_id)
            )
            for barremage in barremages
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def historique_prix_carburants(self, info: strawberry.Info) -> List[HistoriquePrixCarburantType]:
        """Récupère l'historique des prix des carburants accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(HistoriquePrixCarburant).join(Carburant)
        
        if not is_admin:
            query = query.filter(Carburant.compagnie_id == user_company_id)
        
        historiques = query.all()
        return [
            HistoriquePrixCarburantType(
                id=str(historique.id),
                carburant_id=str(historique.carburant_id),
                prix_achat=float(historique.prix_achat or 0) if historique.prix_achat else None,
                prix_vente=float(historique.prix_vente or 0) if historique.prix_vente else None,
                date_application=historique.date_application.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                created_at=historique.created_at.isoformat()
            )
            for historique in historiques
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def historique_prix_articles(self, info: strawberry.Info) -> List[HistoriquePrixArticleType]:
        """Récupère l'historique des prix des articles accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(HistoriquePrixArticle).join(Article)
        
        if not is_admin:
            query = query.filter(Article.compagnie_id == user_company_id)
        
        historiques = query.all()
        return [
            HistoriquePrixArticleType(
                id=str(historique.id),
                article_id=str(historique.article_id),
                prix_achat=float(historique.prix_achat or 0) if historique.prix_achat else None,
                prix_vente=float(historique.prix_vente or 0) if historique.prix_vente else None,
                date_application=historique.date_application.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                created_at=historique.created_at.isoformat()
            )
            for historique in historiques
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def historique_index_pistolets(self, info: strawberry.Info) -> List[HistoriqueIndexPistoletType]:
        """Récupère l'historique des index des pistolets accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(HistoriqueIndexPistolet).join(Pistolet)
        
        if not is_admin:
            query = query.filter(Pistolet.compagnie_id == user_company_id)
        
        historiques = query.all()
        return [
            HistoriqueIndexPistoletType(
                id=str(historique.id),
                pistolet_id=str(historique.pistolet_id),
                index_releve=float(historique.index_releve or 0),
                date_releve=historique.date_releve.isoformat(),
                utilisateur_id=str(historique.utilisateur_id) if historique.utilisateur_id else None,
                observation=historique.observation,
                statut=historique.statut,
                created_at=historique.created_at.isoformat()
            )
            for historique in historiques
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def familles_articles(self, info: strawberry.Info) -> List[FamilleArticleType]:
        """Récupère toutes les familles d'articles accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(FamilleArticle)
        
        if not is_admin:
            query = query.filter(FamilleArticle.compagnie_id == user_company_id)
        
        familles = query.all()
        return [
            FamilleArticleType(
                id=str(famille.id),
                code=famille.code,
                libelle=famille.libelle,
                compagnie_id=str(famille.compagnie_id),
                statut=famille.statut,
                parent_id=str(famille.parent_id) if famille.parent_id else None,
                created_at=famille.created_at.isoformat(),
                updated_at=famille.updated_at.isoformat() if famille.updated_at else None
            )
            for famille in familles
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def articles(self, info: strawberry.Info) -> List[ArticleType]:
        """Récupère tous les articles accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Article)
        
        if not is_admin:
            query = query.filter(Article.compagnie_id == user_company_id)
        
        articles = query.all()
        return [
            ArticleType(
                id=str(article.id),
                code=article.code,
                libelle=article.libelle,
                codebarre=article.codebarre,
                famille_id=str(article.famille_id) if article.famille_id else None,
                unite=article.unite,
                unite_principale=article.unite_principale,
                unite_stock=article.unite_stock,
                compagnie_id=str(article.compagnie_id),
                type_article=article.type_article,
                prix_achat=float(article.prix_achat or 0) if article.prix_achat else None,
                prix_vente=float(article.prix_vente or 0) if article.prix_vente else None,
                tva=float(article.tva or 0) if article.tva else None,
                taxes_applicables=article.taxes_applicables if article.taxes_applicables else None,
                stock_minimal=float(article.stock_minimal or 0) if article.stock_minimal else None,
                statut=article.statut,
                created_at=article.created_at.isoformat(),
                updated_at=article.updated_at.isoformat() if article.updated_at else None
            )
            for article in articles
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def fournisseurs(self, info: strawberry.Info) -> List[FournisseurType]:
        """Récupère tous les fournisseurs accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Fournisseur)
        
        if not is_admin:
            query = query.filter(Fournisseur.compagnie_id == user_company_id)
        
        fournisseurs = query.all()
        return [
            FournisseurType(
                id=str(fournisseur.id),
                code=fournisseur.code,
                nom=fournisseur.nom,
                adresse=fournisseur.adresse,
                telephone=fournisseur.telephone,
                nif=fournisseur.nif,
                email=fournisseur.email,
                compagnie_id=str(fournisseur.compagnie_id),
                station_ids=fournisseur.station_ids if fournisseur.station_ids else None,
                type_tiers_id=str(fournisseur.type_tiers_id) if fournisseur.type_tiers_id else None,
                statut=fournisseur.statut,
                nb_jrs_creance=fournisseur.nb_jrs_creance,
                solde_comptable=float(fournisseur.solde_comptable or 0) if fournisseur.solde_comptable else None,
                solde_confirme=float(fournisseur.solde_confirme or 0) if fournisseur.solde_confirme else None,
                date_dernier_rapprochement=fournisseur.date_dernier_rapprochement.isoformat() if fournisseur.date_dernier_rapprochement else None,
                created_at=fournisseur.created_at.isoformat(),
                updated_at=fournisseur.updated_at.isoformat() if fournisseur.updated_at else None
            )
            for fournisseur in fournisseurs
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def clients(self, info: strawberry.Info) -> List[ClientType]:
        """Récupère tous les clients accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Client)
        
        if not is_admin:
            query = query.filter(Client.compagnie_id == user_company_id)
        
        clients = query.all()
        return [
            ClientType(
                id=str(client.id),
                code=client.code,
                nom=client.nom,
                adresse=client.adresse,
                telephone=client.telephone,
                nif=client.nif,
                email=client.email,
                compagnie_id=str(client.compagnie_id),
                station_ids=client.station_ids if client.station_ids else None,
                type_tiers_id=str(client.type_tiers_id) if client.type_tiers_id else None,
                statut=client.statut,
                nb_jrs_creance=client.nb_jrs_creance,
                solde_comptable=float(client.solde_comptable or 0) if client.solde_comptable else None,
                solde_confirme=float(client.solde_confirme or 0) if client.solde_confirme else None,
                date_dernier_rapprochement=client.date_dernier_rapprochement.isoformat() if client.date_dernier_rapprochement else None,
                devise_facturation=client.devise_facturation,
                created_at=client.created_at.isoformat(),
                updated_at=client.updated_at.isoformat() if client.updated_at else None
            )
            for client in clients
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def employes(self, info: strawberry.Info) -> List[EmployeType]:
        """Récupère tous les employés accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Employe)
        
        if not is_admin:
            query = query.filter(Employe.compagnie_id == user_company_id)
        
        employes = query.all()
        return [
            EmployeType(
                id=str(employe.id),
                code=employe.code,
                nom=employe.nom,
                prenom=employe.prenom,
                adresse=employe.adresse,
                telephone=employe.telephone,
                poste=employe.poste,
                salaire_base=float(employe.salaire_base or 0) if employe.salaire_base else None,
                avances=float(employe.avances or 0) if employe.avances else None,
                creances=float(employe.creances or 0) if employe.creances else None,
                station_ids=employe.station_ids if employe.station_ids else None,
                compagnie_id=str(employe.compagnie_id),
                statut=employe.statut,
                created_at=employe.created_at.isoformat(),
                updated_at=employe.updated_at.isoformat() if employe.updated_at else None
            )
            for employe in employes
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def tresoreries(self, info: strawberry.Info) -> List[TresorerieType]:
        """Récupère toutes les trésoreries accessibles par l'utilisateur"""
        user_company_id = await get_current_user_company_id(info)
        is_admin = info.context.is_admin_or_super_admin
        
        session = info.context.db_session
        query = session.query(Tresorerie)
        
        if not is_admin:
            query = query.filter(Tresorerie.compagnie_id == user_company_id)
        
        tresoreries = query.all()
        return [
            TresorerieType(
                id=str(tresorerie.id),
                code=tresorerie.code,
                libelle=tresorerie.libelle,
                compagnie_id=str(tresorerie.compagnie_id),
                station_ids=tresorerie.station_ids if tresorerie.station_ids else None,
                solde=float(tresorerie.solde or 0) if tresorerie.solde else None,
                devise_code=tresorerie.devise_code,
                taux_change=float(tresorerie.taux_change or 0) if tresorerie.taux_change else None,
                fournisseur_id=str(tresorerie.fournisseur_id) if tresorerie.fournisseur_id else None,
                type_tresorerie=str(tresorerie.type_tresorerie) if tresorerie.type_tresorerie else None,
                methode_paiement=tresorerie.methode_paiement if tresorerie.methode_paiement else None,
                statut=tresorerie.statut,
                solde_theorique=float(tresorerie.solde_theorique or 0) if tresorerie.solde_theorique else None,
                solde_reel=float(tresorerie.solde_reel or 0) if tresorerie.solde_reel else None,
                date_dernier_rapprochement=tresorerie.date_dernier_rapprochement.isoformat() if tresorerie.date_dernier_rapprochement else None,
                utilisateur_dernier_rapprochement=str(tresorerie.utilisateur_dernier_rapprochement) if tresorerie.utilisateur_dernier_rapprochement else None,
                type_tresorerie_libelle=tresorerie.type_tresorerie_libelle,
                created_at=tresorerie.created_at.isoformat(),
                updated_at=tresorerie.updated_at.isoformat() if tresorerie.updated_at else None
            )
            for tresorerie in tresoreries
        ]


# Pour l'instant, je n'ai implémenté que les requêtes (Query), pas les mutations (création, modification, suppression)
# car cela nécessiterait des types d'input et une logique de validation plus complexes