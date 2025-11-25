import strawberry
from typing import List, Optional
from models.achats import (
    Achat as AchatModel,
    AchatDetail as AchatDetailModel,
    BonCommande as BonCommandeModel
)
from strawberry_graphql.types.achats import (
    Achat,
    AchatDetail,
    BonCommande
)
from strawberry_graphql.context import GraphQLContext

@strawberry.type
class AchatQuery:
    @strawberry.field
    def achat(self, info, achat_id: str) -> Optional[Achat]:
        context: GraphQLContext = info.context
        db_achat = context.db_session.query(AchatModel).filter(AchatModel.id == achat_id).first()
        if db_achat:
            return Achat.from_instance(db_achat)
        return None

    @strawberry.field
    def all_achats(self, info) -> List[Achat]:
        context: GraphQLContext = info.context
        db_achat_list = context.db_session.query(AchatModel).all()
        return [Achat.from_instance(achat) for achat in db_achat_list]

    @strawberry.field
    def achat_detail(self, info, achat_detail_id: str) -> Optional[AchatDetail]:
        context: GraphQLContext = info.context
        db_achat_detail = context.db_session.query(AchatDetailModel).filter(AchatDetailModel.id == achat_detail_id).first()
        if db_achat_detail:
            return AchatDetail.from_instance(db_achat_detail)
        return None

    @strawberry.field
    def all_achat_details(self, info) -> List[AchatDetail]:
        context: GraphQLContext = info.context
        db_achat_detail_list = context.db_session.query(AchatDetailModel).all()
        return [AchatDetail.from_instance(achat_detail) for achat_detail in db_achat_detail_list]

    @strawberry.field
    def bon_commande(self, info, bon_commande_id: str) -> Optional[BonCommande]:
        context: GraphQLContext = info.context
        db_bon_commande = context.db_session.query(BonCommandeModel).filter(BonCommandeModel.id == bon_commande_id).first()
        if db_bon_commande:
            return BonCommande.from_instance(db_bon_commande)
        return None

    @strawberry.field
    def all_bons_commande(self, info) -> List[BonCommande]:
        context: GraphQLContext = info.context
        db_bon_commande_list = context.db_session.query(BonCommandeModel).all()
        return [BonCommande.from_instance(bon_commande) for bon_commande in db_bon_commande_list]

@strawberry.type
class AchatMutation:
    pass

# Combiner Query et Mutation
achat_query = AchatQuery
achat_mutation = AchatMutation