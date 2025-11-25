import strawberry
from typing import List, Optional
from models.stocks import (
    MouvementStock as MouvementStockModel,
    MouvementStockDetail as MouvementStockDetailModel,
    Inventaire as InventaireModel,
    InventaireDetail as InventaireDetailModel,
    TransfertStock as TransfertStockModel,
    TransfertStockDetail as TransfertStockDetailModel
)
from strawberry_graphql.types.stocks import (
    MouvementStock,
    MouvementStockDetail,
    Inventaire,
    InventaireDetail,
    TransfertStock,
    TransfertStockDetail
)
from strawberry_graphql.context import GraphQLContext

@strawberry.type
class StockQuery:
    @strawberry.field
    def mouvement_stock(self, info, mouvement_stock_id: str) -> Optional[MouvementStock]:
        context: GraphQLContext = info.context
        db_mouvement_stock = context.db_session.query(MouvementStockModel).filter(MouvementStockModel.id == mouvement_stock_id).first()
        if db_mouvement_stock:
            return MouvementStock.from_instance(db_mouvement_stock)
        return None

    @strawberry.field
    def all_mouvements_stock(self, info) -> List[MouvementStock]:
        context: GraphQLContext = info.context
        db_mouvement_stock_list = context.db_session.query(MouvementStockModel).all()
        return [MouvementStock.from_instance(mouvement_stock) for mouvement_stock in db_mouvement_stock_list]

    @strawberry.field
    def mouvement_stock_detail(self, info, mouvement_stock_detail_id: str) -> Optional[MouvementStockDetail]:
        context: GraphQLContext = info.context
        db_mouvement_stock_detail = context.db_session.query(MouvementStockDetailModel).filter(MouvementStockDetailModel.id == mouvement_stock_detail_id).first()
        if db_mouvement_stock_detail:
            return MouvementStockDetail.from_instance(db_mouvement_stock_detail)
        return None

    @strawberry.field
    def all_mouvement_stock_details(self, info) -> List[MouvementStockDetail]:
        context: GraphQLContext = info.context
        db_mouvement_stock_detail_list = context.db_session.query(MouvementStockDetailModel).all()
        return [MouvementStockDetail.from_instance(mouvement_stock_detail) for mouvement_stock_detail in db_mouvement_stock_detail_list]

    @strawberry.field
    def inventaire(self, info, inventaire_id: str) -> Optional[Inventaire]:
        context: GraphQLContext = info.context
        db_inventaire = context.db_session.query(InventaireModel).filter(InventaireModel.id == inventaire_id).first()
        if db_inventaire:
            return Inventaire.from_instance(db_inventaire)
        return None

    @strawberry.field
    def all_inventaires(self, info) -> List[Inventaire]:
        context: GraphQLContext = info.context
        db_inventaire_list = context.db_session.query(InventaireModel).all()
        return [Inventaire.from_instance(inventaire) for inventaire in db_inventaire_list]

    @strawberry.field
    def inventaire_detail(self, info, inventaire_detail_id: str) -> Optional[InventaireDetail]:
        context: GraphQLContext = info.context
        db_inventaire_detail = context.db_session.query(InventaireDetailModel).filter(InventaireDetailModel.id == inventaire_detail_id).first()
        if db_inventaire_detail:
            return InventaireDetail.from_instance(db_inventaire_detail)
        return None

    @strawberry.field
    def all_inventaire_details(self, info) -> List[InventaireDetail]:
        context: GraphQLContext = info.context
        db_inventaire_detail_list = context.db_session.query(InventaireDetailModel).all()
        return [InventaireDetail.from_instance(inventaire_detail) for inventaire_detail in db_inventaire_detail_list]

    @strawberry.field
    def transfert_stock(self, info, transfert_stock_id: str) -> Optional[TransfertStock]:
        context: GraphQLContext = info.context
        db_transfert_stock = context.db_session.query(TransfertStockModel).filter(TransfertStockModel.id == transfert_stock_id).first()
        if db_transfert_stock:
            return TransfertStock.from_instance(db_transfert_stock)
        return None

    @strawberry.field
    def all_transferts_stock(self, info) -> List[TransfertStock]:
        context: GraphQLContext = info.context
        db_transfert_stock_list = context.db_session.query(TransfertStockModel).all()
        return [TransfertStock.from_instance(transfert_stock) for transfert_stock in db_transfert_stock_list]

    @strawberry.field
    def transfert_stock_detail(self, info, transfert_stock_detail_id: str) -> Optional[TransfertStockDetail]:
        context: GraphQLContext = info.context
        db_transfert_stock_detail = context.db_session.query(TransfertStockDetailModel).filter(TransfertStockDetailModel.id == transfert_stock_detail_id).first()
        if db_transfert_stock_detail:
            return TransfertStockDetail.from_instance(db_transfert_stock_detail)
        return None

    @strawberry.field
    def all_transfert_stock_details(self, info) -> List[TransfertStockDetail]:
        context: GraphQLContext = info.context
        db_transfert_stock_detail_list = context.db_session.query(TransfertStockDetailModel).all()
        return [TransfertStockDetail.from_instance(transfert_stock_detail) for transfert_stock_detail in db_transfert_stock_detail_list]

@strawberry.type
class StockMutation:
    pass

# Combiner Query et Mutation
stock_query = StockQuery
stock_mutation = StockMutation