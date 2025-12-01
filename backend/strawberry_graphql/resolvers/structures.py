import strawberry
from typing import List, Optional
from models.structures import (
    Pays as PaysModel,
    Compagnie as CompagnieModel,
    Station as StationModel,
    Utilisateur as UtilisateurModel,
    Article as ArticleModel,
    Carburant as CarburantModel,
    Cuve as CuveModel,
    Pompe as PompeModel,
    Pistolet as PistoletModel,
    Client as ClientModel,
    Fournisseur as FournisseurModel,
    Employe as EmployeModel,
    Tresorerie as TresorerieModel,
    BarremageCuve as BarremageCuveModel,
    HistoriquePrixCarburant as HistoriquePrixCarburantModel,
    HistoriquePrixArticle as HistoriquePrixArticleModel,
    HistoriqueIndexPistolet as HistoriqueIndexPistoletModel,
    FamilleArticle as FamilleArticleModel
)
from strawberry_graphql.types.structures import (
    Pays,
    Compagnie,
    Station,
    Utilisateur,
    Article,
    Carburant,
    Cuve,
    Pompe,
    Pistolet,
    Client,
    Fournisseur,
    Employe,
    BarremageCuve,
    HistoriquePrixCarburant,
    HistoriquePrixArticle,
    HistoriqueIndexPistolet,
    FamilleArticle
)
from strawberry_graphql.context import GraphQLContext
from strawberry_graphql.utils import filter_query_by_user_company, check_user_access_to_company_resource
from fastapi import HTTPException

@strawberry.type
class Query:
    @strawberry.field
    def pays(self, info, pays_id: str) -> Optional[Pays]:
        context: GraphQLContext = info.context
        # Seuls les administrateurs peuvent accéder aux données pays
        if context.current_user and not context.current_user.type_utilisateur in ["super_administrateur", "administrateur"]:
            raise HTTPException(status_code=403, detail="Access to countries information is restricted to admin users")

        db_pays = context.db_session.query(PaysModel).filter(PaysModel.id == pays_id).first()
        if db_pays:
            return Pays.from_instance(db_pays)
        return None

    @strawberry.field
    def all_pays(self, info) -> List[Pays]:
        context: GraphQLContext = info.context
        # Seuls les administrateurs peuvent accéder aux données pays
        if context.current_user and not context.current_user.type_utilisateur in ["super_administrateur", "administrateur"]:
            raise HTTPException(status_code=403, detail="Access to countries information is restricted to admin users")

        db_pays_list = context.db_session.query(PaysModel).all()
        return [Pays.from_instance(pays) for pays in db_pays_list]

    @strawberry.field
    def compagnie(self, info, compagnie_id: str) -> Optional[Compagnie]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_compagnie = context.db_session.query(CompagnieModel).filter(CompagnieModel.id == compagnie_id).first()

        if db_compagnie:
            # Vérifier que l'utilisateur a accès à cette compagnie
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_compagnie.id)
            )

            if has_access:
                return Compagnie.from_instance(db_compagnie)

        return None

    @strawberry.field
    def all_compagnies(self, info) -> List[Compagnie]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(CompagnieModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, CompagnieModel, context.current_user)

        db_compagnie_list = query.all()
        return [Compagnie.from_instance(compagnie) for compagnie in db_compagnie_list]

    @strawberry.field
    def station(self, info, station_id: str) -> Optional[Station]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_station = context.db_session.query(StationModel).filter(StationModel.id == station_id).first()

        if db_station:
            # Vérifier que l'utilisateur a accès à cette station
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_station.compagnie_id)
            )

            if has_access:
                return Station.from_instance(db_station)

        return None

    @strawberry.field
    def all_stations(self, info) -> List[Station]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(StationModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, StationModel, context.current_user)

        db_station_list = query.all()
        return [Station.from_instance(station) for station in db_station_list]

    @strawberry.field
    def utilisateur(self, info, utilisateur_id: str) -> Optional[Utilisateur]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_utilisateur = context.db_session.query(UtilisateurModel).filter(UtilisateurModel.id == utilisateur_id).first()

        if db_utilisateur:
            # Vérifier que l'utilisateur a accès à cet utilisateur (appartenance à la même compagnie)
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_utilisateur.compagnie_id)
            )

            if has_access:
                return Utilisateur.from_instance(db_utilisateur)

        return None

    @strawberry.field
    def all_utilisateurs(self, info) -> List[Utilisateur]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(UtilisateurModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, UtilisateurModel, context.current_user)

        db_utilisateur_list = query.all()
        return [Utilisateur.from_instance(utilisateur) for utilisateur in db_utilisateur_list]

    @strawberry.field
    def article(self, info, article_id: str) -> Optional[Article]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_article = context.db_session.query(ArticleModel).filter(ArticleModel.id == article_id).first()

        if db_article:
            # Vérifier que l'utilisateur a accès à cet article
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_article.compagnie_id)
            )

            if has_access:
                return Article.from_instance(db_article)

        return None

    @strawberry.field
    def all_articles(self, info) -> List[Article]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(ArticleModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, ArticleModel, context.current_user)

        db_article_list = query.all()
        return [Article.from_instance(article) for article in db_article_list]

    @strawberry.field
    def carburant(self, info, carburant_id: str) -> Optional[Carburant]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_carburant = context.db_session.query(CarburantModel).filter(CarburantModel.id == carburant_id).first()

        if db_carburant:
            # Vérifier que l'utilisateur a accès à ce carburant
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_carburant.compagnie_id)
            )

            if has_access:
                return Carburant.from_instance(db_carburant)

        return None

    @strawberry.field
    def all_carburants(self, info) -> List[Carburant]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(CarburantModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, CarburantModel, context.current_user)

        db_carburant_list = query.all()
        return [Carburant.from_instance(carburant) for carburant in db_carburant_list]

    @strawberry.field
    def cuve(self, info, cuve_id: str) -> Optional[Cuve]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_cuve = context.db_session.query(CuveModel).filter(CuveModel.id == cuve_id).first()

        if db_cuve:
            # Vérifier que l'utilisateur a accès à cette cuve
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_cuve.compagnie_id)
            )

            if has_access:
                return Cuve.from_instance(db_cuve)

        return None

    @strawberry.field
    def all_cuves(self, info) -> List[Cuve]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(CuveModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, CuveModel, context.current_user)

        db_cuve_list = query.all()
        return [Cuve.from_instance(cuve) for cuve in db_cuve_list]

    @strawberry.field
    def pompe(self, info, pompe_id: str) -> Optional[Pompe]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_pompe = context.db_session.query(PompeModel).filter(PompeModel.id == pompe_id).first()

        if db_pompe:
            # Vérifier que l'utilisateur a accès à cette pompe
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_pompe.compagnie_id)
            )

            if has_access:
                return Pompe.from_instance(db_pompe)

        return None

    @strawberry.field
    def all_pompes(self, info) -> List[Pompe]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(PompeModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, PompeModel, context.current_user)

        db_pompe_list = query.all()
        return [Pompe.from_instance(pompe) for pompe in db_pompe_list]

    @strawberry.field
    def pistolet(self, info, pistolet_id: str) -> Optional[Pistolet]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_pistolet = context.db_session.query(PistoletModel).filter(PistoletModel.id == pistolet_id).first()

        if db_pistolet:
            # Vérifier que l'utilisateur a accès à ce pistolet
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_pistolet.compagnie_id)
            )

            if has_access:
                return Pistolet.from_instance(db_pistolet)

        return None

    @strawberry.field
    def all_pistolets(self, info) -> List[Pistolet]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(PistoletModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, PistoletModel, context.current_user)

        db_pistolet_list = query.all()
        return [Pistolet.from_instance(pistolet) for pistolet in db_pistolet_list]

    @strawberry.field
    def client(self, info, client_id: str) -> Optional[Client]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_client = context.db_session.query(ClientModel).filter(ClientModel.id == client_id).first()

        if db_client:
            # Vérifier que l'utilisateur a accès à ce client
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_client.compagnie_id)
            )

            if has_access:
                return Client.from_instance(db_client)

        return None

    @strawberry.field
    def all_clients(self, info) -> List[Client]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(ClientModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, ClientModel, context.current_user)

        db_client_list = query.all()
        return [Client.from_instance(client) for client in db_client_list]

    @strawberry.field
    def fournisseur(self, info, fournisseur_id: str) -> Optional[Fournisseur]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_fournisseur = context.db_session.query(FournisseurModel).filter(FournisseurModel.id == fournisseur_id).first()

        if db_fournisseur:
            # Vérifier que l'utilisateur a accès à ce fournisseur
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_fournisseur.compagnie_id)
            )

            if has_access:
                return Fournisseur.from_instance(db_fournisseur)

        return None

    @strawberry.field
    def all_fournisseurs(self, info) -> List[Fournisseur]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(FournisseurModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, FournisseurModel, context.current_user)

        db_fournisseur_list = query.all()
        return [Fournisseur.from_instance(fournisseur) for fournisseur in db_fournisseur_list]

    @strawberry.field
    def employe(self, info, employe_id: str) -> Optional[Employe]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db_employe = context.db_session.query(EmployeModel).filter(EmployeModel.id == employe_id).first()

        if db_employe:
            # Vérifier que l'utilisateur a accès à cet employé
            has_access = check_user_access_to_company_resource(
                context.db_session,
                context.current_user,
                str(db_employe.compagnie_id)
            )

            if has_access:
                return Employe.from_instance(db_employe)

        return None

    @strawberry.field
    def all_employes(self, info) -> List[Employe]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(EmployeModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, EmployeModel, context.current_user)

        db_employe_list = query.all()
        return [Employe.from_instance(employe) for employe in db_employe_list]

    @strawberry.field
    def barremage_cuves(self, info) -> List[BarremageCuve]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(BarremageCuveModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, BarremageCuveModel, context.current_user)

        db_barremage_cuves_list = query.all()
        return [BarremageCuve.from_instance(barremage) for barremage in db_barremage_cuves_list]

    @strawberry.field
    def historique_prix_carburants(self, info) -> List[HistoriquePrixCarburant]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(HistoriquePrixCarburantModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, HistoriquePrixCarburantModel, context.current_user)

        db_historique_list = query.all()
        return [HistoriquePrixCarburant.from_instance(historique) for historique in db_historique_list]

    @strawberry.field
    def historique_prix_articles(self, info) -> List[HistoriquePrixArticle]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(HistoriquePrixArticleModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, HistoriquePrixArticleModel, context.current_user)

        db_historique_list = query.all()
        return [HistoriquePrixArticle.from_instance(historique) for historique in db_historique_list]

    @strawberry.field
    def historique_index_pistolets(self, info) -> List[HistoriqueIndexPistolet]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(HistoriqueIndexPistoletModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, HistoriqueIndexPistoletModel, context.current_user)

        db_historique_list = query.all()
        return [HistoriqueIndexPistolet.from_instance(historique) for historique in db_historique_list]

    @strawberry.field
    def all_familles_articles(self, info) -> List[FamilleArticle]:
        context: GraphQLContext = info.context
        if not context.current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        query = context.db_session.query(FamilleArticleModel)

        # Filtrer les résultats selon la compagnie de l'utilisateur (sauf pour les administrateurs)
        query = filter_query_by_user_company(query, FamilleArticleModel, context.current_user)

        db_famille_list = query.all()
        return [FamilleArticle.from_instance(famille) for famille in db_famille_list]

@strawberry.type
class Mutation:
    pass

# Combiner Query et Mutation
schema_query = Query
schema_mutation = Mutation