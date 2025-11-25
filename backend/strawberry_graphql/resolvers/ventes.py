import strawberry
from typing import List, Optional
from models.ventes import (
    Vente as VenteModel,
    VenteDetail as VenteDetailModel,
    Reglement as ReglementModel
)
from strawberry_graphql.types.ventes import (
    Vente,
    VenteDetail,
    Reglement
)
from strawberry_graphql.context import GraphQLContext

@strawberry.type
class VenteQuery:
    @strawberry.field
    def vente(self, info, vente_id: str) -> Optional[Vente]:
        context: GraphQLContext = info.context
        db_vente = context.db_session.query(VenteModel).filter(VenteModel.id == vente_id).first()
        if db_vente:
            return Vente.from_instance(db_vente)
        return None

    @strawberry.field
    def all_ventes(self, info) -> List[Vente]:
        context: GraphQLContext = info.context
        db_vente_list = context.db_session.query(VenteModel).all()
        return [Vente.from_instance(vente) for vente in db_vente_list]

    @strawberry.field
    def vente_detail(self, info, vente_detail_id: str) -> Optional[VenteDetail]:
        context: GraphQLContext = info.context
        db_vente_detail = context.db_session.query(VenteDetailModel).filter(VenteDetailModel.id == vente_detail_id).first()
        if db_vente_detail:
            return VenteDetail.from_instance(db_vente_detail)
        return None

    @strawberry.field
    def all_vente_details(self, info) -> List[VenteDetail]:
        context: GraphQLContext = info.context
        db_vente_detail_list = context.db_session.query(VenteDetailModel).all()
        return [VenteDetail.from_instance(vente_detail) for vente_detail in db_vente_detail_list]

    @strawberry.field
    def reglement(self, info, reglement_id: str) -> Optional[Reglement]:
        context: GraphQLContext = info.context
        db_reglement = context.db_session.query(ReglementModel).filter(ReglementModel.id == reglement_id).first()
        if db_reglement:
            return Reglement.from_instance(db_reglement)
        return None

    @strawberry.field
    def all_reglements(self, info) -> List[Reglement]:
        context: GraphQLContext = info.context
        db_reglement_list = context.db_session.query(ReglementModel).all()
        return [Reglement.from_instance(reglement) for reglement in db_reglement_list]

@strawberry.type
class VenteMutation:
    pass

# Combiner Query et Mutation
vente_query = VenteQuery
vente_mutation = VenteMutation