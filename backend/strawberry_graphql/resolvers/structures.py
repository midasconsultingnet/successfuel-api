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
    Employe as EmployeModel
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
    Employe
)
from strawberry_graphql.context import GraphQLContext

@strawberry.type
class Query:
    @strawberry.field
    def pays(self, info, pays_id: str) -> Optional[Pays]:
        context: GraphQLContext = info.context
        db_pays = context.db_session.query(PaysModel).filter(PaysModel.id == pays_id).first()
        if db_pays:
            return Pays.from_instance(db_pays)
        return None

    @strawberry.field
    def all_pays(self, info) -> List[Pays]:
        context: GraphQLContext = info.context
        db_pays_list = context.db_session.query(PaysModel).all()
        return [Pays.from_instance(pays) for pays in db_pays_list]

    @strawberry.field
    def compagnie(self, info, compagnie_id: str) -> Optional[Compagnie]:
        context: GraphQLContext = info.context
        db_compagnie = context.db_session.query(CompagnieModel).filter(CompagnieModel.id == compagnie_id).first()
        if db_compagnie:
            return Compagnie.from_instance(db_compagnie)
        return None

    @strawberry.field
    def all_compagnies(self, info) -> List[Compagnie]:
        context: GraphQLContext = info.context
        db_compagnie_list = context.db_session.query(CompagnieModel).all()
        return [Compagnie.from_instance(compagnie) for compagnie in db_compagnie_list]

    @strawberry.field
    def station(self, info, station_id: str) -> Optional[Station]:
        context: GraphQLContext = info.context
        db_station = context.db_session.query(StationModel).filter(StationModel.id == station_id).first()
        if db_station:
            return Station.from_instance(db_station)
        return None

    @strawberry.field
    def all_stations(self, info) -> List[Station]:
        context: GraphQLContext = info.context
        db_station_list = context.db_session.query(StationModel).all()
        return [Station.from_instance(station) for station in db_station_list]

    @strawberry.field
    def utilisateur(self, info, utilisateur_id: str) -> Optional[Utilisateur]:
        context: GraphQLContext = info.context
        db_utilisateur = context.db_session.query(UtilisateurModel).filter(UtilisateurModel.id == utilisateur_id).first()
        if db_utilisateur:
            return Utilisateur.from_instance(db_utilisateur)
        return None

    @strawberry.field
    def all_utilisateurs(self, info) -> List[Utilisateur]:
        context: GraphQLContext = info.context
        db_utilisateur_list = context.db_session.query(UtilisateurModel).all()
        return [Utilisateur.from_instance(utilisateur) for utilisateur in db_utilisateur_list]

    @strawberry.field
    def article(self, info, article_id: str) -> Optional[Article]:
        context: GraphQLContext = info.context
        db_article = context.db_session.query(ArticleModel).filter(ArticleModel.id == article_id).first()
        if db_article:
            return Article.from_instance(db_article)
        return None

    @strawberry.field
    def all_articles(self, info) -> List[Article]:
        context: GraphQLContext = info.context
        db_article_list = context.db_session.query(ArticleModel).all()
        return [Article.from_instance(article) for article in db_article_list]

    @strawberry.field
    def carburant(self, info, carburant_id: str) -> Optional[Carburant]:
        context: GraphQLContext = info.context
        db_carburant = context.db_session.query(CarburantModel).filter(CarburantModel.id == carburant_id).first()
        if db_carburant:
            return Carburant.from_instance(db_carburant)
        return None

    @strawberry.field
    def all_carburants(self, info) -> List[Carburant]:
        context: GraphQLContext = info.context
        db_carburant_list = context.db_session.query(CarburantModel).all()
        return [Carburant.from_instance(carburant) for carburant in db_carburant_list]

    @strawberry.field
    def cuve(self, info, cuve_id: str) -> Optional[Cuve]:
        context: GraphQLContext = info.context
        db_cuve = context.db_session.query(CuveModel).filter(CuveModel.id == cuve_id).first()
        if db_cuve:
            return Cuve.from_instance(db_cuve)
        return None

    @strawberry.field
    def all_cuves(self, info) -> List[Cuve]:
        context: GraphQLContext = info.context
        db_cuve_list = context.db_session.query(CuveModel).all()
        return [Cuve.from_instance(cuve) for cuve in db_cuve_list]

    @strawberry.field
    def pompe(self, info, pompe_id: str) -> Optional[Pompe]:
        context: GraphQLContext = info.context
        db_pompe = context.db_session.query(PompeModel).filter(PompeModel.id == pompe_id).first()
        if db_pompe:
            return Pompe.from_instance(db_pompe)
        return None

    @strawberry.field
    def all_pompes(self, info) -> List[Pompe]:
        context: GraphQLContext = info.context
        db_pompe_list = context.db_session.query(PompeModel).all()
        return [Pompe.from_instance(pompe) for pompe in db_pompe_list]

    @strawberry.field
    def pistolet(self, info, pistolet_id: str) -> Optional[Pistolet]:
        context: GraphQLContext = info.context
        db_pistolet = context.db_session.query(PistoletModel).filter(PistoletModel.id == pistolet_id).first()
        if db_pistolet:
            return Pistolet.from_instance(db_pistolet)
        return None

    @strawberry.field
    def all_pistolets(self, info) -> List[Pistolet]:
        context: GraphQLContext = info.context
        db_pistolet_list = context.db_session.query(PistoletModel).all()
        return [Pistolet.from_instance(pistolet) for pistolet in db_pistolet_list]

    @strawberry.field
    def client(self, info, client_id: str) -> Optional[Client]:
        context: GraphQLContext = info.context
        db_client = context.db_session.query(ClientModel).filter(ClientModel.id == client_id).first()
        if db_client:
            return Client.from_instance(db_client)
        return None

    @strawberry.field
    def all_clients(self, info) -> List[Client]:
        context: GraphQLContext = info.context
        db_client_list = context.db_session.query(ClientModel).all()
        return [Client.from_instance(client) for client in db_client_list]

    @strawberry.field
    def fournisseur(self, info, fournisseur_id: str) -> Optional[Fournisseur]:
        context: GraphQLContext = info.context
        db_fournisseur = context.db_session.query(FournisseurModel).filter(FournisseurModel.id == fournisseur_id).first()
        if db_fournisseur:
            return Fournisseur.from_instance(db_fournisseur)
        return None

    @strawberry.field
    def all_fournisseurs(self, info) -> List[Fournisseur]:
        context: GraphQLContext = info.context
        db_fournisseur_list = context.db_session.query(FournisseurModel).all()
        return [Fournisseur.from_instance(fournisseur) for fournisseur in db_fournisseur_list]

    @strawberry.field
    def employe(self, info, employe_id: str) -> Optional[Employe]:
        context: GraphQLContext = info.context
        db_employe = context.db_session.query(EmployeModel).filter(EmployeModel.id == employe_id).first()
        if db_employe:
            return Employe.from_instance(db_employe)
        return None

    @strawberry.field
    def all_employes(self, info) -> List[Employe]:
        context: GraphQLContext = info.context
        db_employe_list = context.db_session.query(EmployeModel).all()
        return [Employe.from_instance(employe) for employe in db_employe_list]

@strawberry.type
class Mutation:
    pass

# Combiner Query et Mutation
schema_query = Query
schema_mutation = Mutation