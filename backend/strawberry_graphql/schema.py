import strawberry
from strawberry_graphql.resolvers.structures import schema_query as structures_query, schema_mutation as structures_mutation
from strawberry_graphql.resolvers.achats import achat_query, achat_mutation
from strawberry_graphql.resolvers.ventes import vente_query, vente_mutation
from strawberry_graphql.resolvers.stocks import stock_query, stock_mutation
from strawberry_graphql.resolvers.tresoreries import tresorerie_query, tresorerie_mutation
from strawberry_graphql.resolvers.comptabilite import comptabilite_query, comptabilite_mutation

@strawberry.type
class Query(
    structures_query,
    achat_query,
    vente_query,
    stock_query,
    tresorerie_query,
    comptabilite_query
):
    pass

@strawberry.type
class Mutation:
    pass

schema = strawberry.Schema(query=Query)