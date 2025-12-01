import strawberry
from typing import List, Optional
from models.tresoreries import (
    MouvementTresorerie as MouvementTresorerieModel,
    MouvementTresorerieDetail as MouvementTresorerieDetailModel,
    Journal as JournalModel
)

# BilanInitial a été déplacé vers le module stocks
from models.stocks import (
    BilanInitialStocks as BilanInitialModel
)
from strawberry_graphql.types.tresoreries import (
    MouvementTresorerie,
    MouvementTresorerieDetail,
    BilanInitial,
    Journal
)
from strawberry_graphql.context import GraphQLContext

@strawberry.type
class TresorerieQuery:
    @strawberry.field
    def mouvement_tresorerie(self, info, mouvement_tresorerie_id: str) -> Optional[MouvementTresorerie]:
        context: GraphQLContext = info.context
        db_mouvement_tresorerie = context.db_session.query(MouvementTresorerieModel).filter(MouvementTresorerieModel.id == mouvement_tresorerie_id).first()
        if db_mouvement_tresorerie:
            return MouvementTresorerie.from_instance(db_mouvement_tresorerie)
        return None

    @strawberry.field
    def all_mouvements_tresorerie(self, info) -> List[MouvementTresorerie]:
        context: GraphQLContext = info.context
        db_mouvement_tresorerie_list = context.db_session.query(MouvementTresorerieModel).all()
        return [MouvementTresorerie.from_instance(mouvement_tresorerie) for mouvement_tresorerie in db_mouvement_tresorerie_list]

    @strawberry.field
    def mouvement_tresorerie_detail(self, info, mouvement_tresorerie_detail_id: str) -> Optional[MouvementTresorerieDetail]:
        context: GraphQLContext = info.context
        db_mouvement_tresorerie_detail = context.db_session.query(MouvementTresorerieDetailModel).filter(MouvementTresorerieDetailModel.id == mouvement_tresorerie_detail_id).first()
        if db_mouvement_tresorerie_detail:
            return MouvementTresorerieDetail.from_instance(db_mouvement_tresorerie_detail)
        return None

    @strawberry.field
    def all_mouvement_tresorerie_details(self, info) -> List[MouvementTresorerieDetail]:
        context: GraphQLContext = info.context
        db_mouvement_tresorerie_detail_list = context.db_session.query(MouvementTresorerieDetailModel).all()
        return [MouvementTresorerieDetail.from_instance(mouvement_tresorerie_detail) for mouvement_tresorerie_detail in db_mouvement_tresorerie_detail_list]

    @strawberry.field
    def bilan_initial(self, info, bilan_initial_id: str) -> Optional[BilanInitial]:
        context: GraphQLContext = info.context
        db_bilan_initial = context.db_session.query(BilanInitialModel).filter(BilanInitialModel.id == bilan_initial_id).first()
        if db_bilan_initial:
            return BilanInitial.from_instance(db_bilan_initial)
        return None

    @strawberry.field
    def all_bilans_initial(self, info) -> List[BilanInitial]:
        context: GraphQLContext = info.context
        db_bilan_initial_list = context.db_session.query(BilanInitialModel).all()
        return [BilanInitial.from_instance(bilan_initial) for bilan_initial in db_bilan_initial_list]

    @strawberry.field
    def journal(self, info, journal_id: str) -> Optional[Journal]:
        context: GraphQLContext = info.context
        db_journal = context.db_session.query(JournalModel).filter(JournalModel.id == journal_id).first()
        if db_journal:
            return Journal.from_instance(db_journal)
        return None

    @strawberry.field
    def all_journaux(self, info) -> List[Journal]:
        context: GraphQLContext = info.context
        db_journal_list = context.db_session.query(JournalModel).all()
        return [Journal.from_instance(journal) for journal in db_journal_list]

@strawberry.type
class TresorerieMutation:
    pass

# Combiner Query et Mutation
tresorerie_query = TresorerieQuery
tresorerie_mutation = TresorerieMutation