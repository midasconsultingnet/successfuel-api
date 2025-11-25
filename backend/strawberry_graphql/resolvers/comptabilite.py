import strawberry
from typing import List, Optional
from models.comptabilite import (
    JournalEntree as JournalEntreeModel,
    JournalLigne as JournalLigneModel,
    EtatStock as EtatStockModel,
    EtatCaisse as EtatCaisseModel,
    EtatComptable as EtatComptableModel
)
from strawberry_graphql.types.comptabilite import (
    JournalEntree,
    JournalLigne,
    EtatStock,
    EtatCaisse,
    EtatComptable
)
from strawberry_graphql.context import GraphQLContext

@strawberry.type
class ComptabiliteQuery:
    @strawberry.field
    def journal_entree(self, info, journal_entree_id: str) -> Optional[JournalEntree]:
        context: GraphQLContext = info.context
        db_journal_entree = context.db_session.query(JournalEntreeModel).filter(JournalEntreeModel.id == journal_entree_id).first()
        if db_journal_entree:
            return JournalEntree.from_instance(db_journal_entree)
        return None

    @strawberry.field
    def all_journaux_entree(self, info) -> List[JournalEntree]:
        context: GraphQLContext = info.context
        db_journal_entree_list = context.db_session.query(JournalEntreeModel).all()
        return [JournalEntree.from_instance(journal_entree) for journal_entree in db_journal_entree_list]

    @strawberry.field
    def journal_ligne(self, info, journal_ligne_id: str) -> Optional[JournalLigne]:
        context: GraphQLContext = info.context
        db_journal_ligne = context.db_session.query(JournalLigneModel).filter(JournalLigneModel.id == journal_ligne_id).first()
        if db_journal_ligne:
            return JournalLigne.from_instance(db_journal_ligne)
        return None

    @strawberry.field
    def all_journaux_ligne(self, info) -> List[JournalLigne]:
        context: GraphQLContext = info.context
        db_journal_ligne_list = context.db_session.query(JournalLigneModel).all()
        return [JournalLigne.from_instance(journal_ligne) for journal_ligne in db_journal_ligne_list]

    @strawberry.field
    def etat_stock(self, info, etat_stock_id: str) -> Optional[EtatStock]:
        context: GraphQLContext = info.context
        db_etat_stock = context.db_session.query(EtatStockModel).filter(EtatStockModel.id == etat_stock_id).first()
        if db_etat_stock:
            return EtatStock.from_instance(db_etat_stock)
        return None

    @strawberry.field
    def all_etats_stock(self, info) -> List[EtatStock]:
        context: GraphQLContext = info.context
        db_etat_stock_list = context.db_session.query(EtatStockModel).all()
        return [EtatStock.from_instance(etat_stock) for etat_stock in db_etat_stock_list]

    @strawberry.field
    def etat_caisse(self, info, etat_caisse_id: str) -> Optional[EtatCaisse]:
        context: GraphQLContext = info.context
        db_etat_caisse = context.db_session.query(EtatCaisseModel).filter(EtatCaisseModel.id == etat_caisse_id).first()
        if db_etat_caisse:
            return EtatCaisse.from_instance(db_etat_caisse)
        return None

    @strawberry.field
    def all_etats_caisse(self, info) -> List[EtatCaisse]:
        context: GraphQLContext = info.context
        db_etat_caisse_list = context.db_session.query(EtatCaisseModel).all()
        return [EtatCaisse.from_instance(etat_caisse) for etat_caisse in db_etat_caisse_list]

    @strawberry.field
    def etat_comptable(self, info, etat_comptable_id: str) -> Optional[EtatComptable]:
        context: GraphQLContext = info.context
        db_etat_comptable = context.db_session.query(EtatComptableModel).filter(EtatComptableModel.id == etat_comptable_id).first()
        if db_etat_comptable:
            return EtatComptable.from_instance(db_etat_comptable)
        return None

    @strawberry.field
    def all_etats_comptable(self, info) -> List[EtatComptable]:
        context: GraphQLContext = info.context
        db_etat_comptable_list = context.db_session.query(EtatComptableModel).all()
        return [EtatComptable.from_instance(etat_comptable) for etat_comptable in db_etat_comptable_list]

@strawberry.type
class ComptabiliteMutation:
    pass

# Combiner Query et Mutation
comptabilite_query = ComptabiliteQuery
comptabilite_mutation = ComptabiliteMutation