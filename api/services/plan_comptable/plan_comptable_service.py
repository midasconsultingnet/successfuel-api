from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from uuid import UUID
from ...database.transaction_manager import transaction
from ...services.database_service import DatabaseService
from ...models.plan_comptable import PlanComptableModel
from ...plan_comptable.schemas import PlanComptableCreate, PlanComptableUpdate, PlanComptableResponse

class PlanComptableService(DatabaseService):
    def __init__(self, db: Session):
        super().__init__(db, PlanComptableModel)

    def create_plan_comptable(self, plan_data: PlanComptableCreate) -> PlanComptableResponse:
        """Créer un nouveau compte dans le plan comptable"""
        # Vérifier si le numéro de compte existe déjà (seulement s'il est fourni)
        if plan_data.numero_compte:
            existing_account = self.db.query(PlanComptableModel).filter(
                PlanComptableModel.numero_compte == plan_data.numero_compte
            ).first()

            if existing_account:
                raise ValueError(f"Le numéro de compte {plan_data.numero_compte} existe déjà.")

        # Vérifier si le parent_id existe (si fourni)
        if plan_data.parent_id:
            parent_account = self.get_by_id(plan_data.parent_id)
            if not parent_account:
                raise ValueError(f"Le compte parent avec l'ID {plan_data.parent_id} n'existe pas.")

            # Si parent_id est fourni, alors compagnie_id doit être fourni
            if not plan_data.compagnie_id:
                raise ValueError("Le champ 'compagnie_id' est requis lorsqu'un 'parent_id' est spécifié.")
        else:
            # Si parent_id n'est pas fourni, alors compagnie_id doit être nul
            if plan_data.compagnie_id:
                raise ValueError("Le champ 'compagnie_id' ne doit pas être spécifié lorsqu'aucun 'parent_id' n'est fourni.")

        # Créer le nouveau compte
        new_plan = PlanComptableModel(**plan_data.dict())

        with transaction(self.db) as session:
            session.add(new_plan)
            session.flush()  # Pour obtenir l'ID avant le commit

            # Convertir en objet de réponse
            response_obj = PlanComptableResponse.from_orm(new_plan)

        return response_obj

    def get_plan_comptable(self, plan_id: UUID) -> Optional[PlanComptableResponse]:
        """Récupérer un compte par son ID"""
        plan = self.get_by_id(plan_id)
        if plan:
            return PlanComptableResponse.from_orm(plan)
        return None

    def update_plan_comptable(self, plan_id: UUID, plan_data: PlanComptableUpdate) -> Optional[PlanComptableResponse]:
        """Mettre à jour un compte existant"""
        plan = self.get_by_id(plan_id)
        if not plan:
            return None

        # Vérifier si le nouveau numéro de compte n'est pas déjà utilisé par un autre compte
        if plan_data.numero_compte and plan_data.numero_compte != plan.numero_compte:
            existing_account = self.db.query(PlanComptableModel).filter(
                PlanComptableModel.numero_compte == plan_data.numero_compte,
                PlanComptableModel.id != plan_id  # Exclure le compte actuel
            ).first()

            if existing_account:
                raise ValueError(f"Le numéro de compte {plan_data.numero_compte} est déjà utilisé par un autre compte.")

        # Vérifier si le nouveau parent_id existe (si fourni)
        if plan_data.parent_id and plan_data.parent_id != plan.parent_id:
            parent_account = self.get_by_id(plan_data.parent_id)
            if not parent_account:
                raise ValueError(f"Le compte parent avec l'ID {plan_data.parent_id} n'existe pas.")

            # Si parent_id est modifié, alors compagnie_id doit être fourni
            if not plan_data.compagnie_id:
                raise ValueError("Le champ 'compagnie_id' est requis lorsqu'un 'parent_id' est spécifié.")
        elif plan_data.parent_id is None and plan.parent_id is not None:
            # Si parent_id est modifié pour devenir NULL, alors compagnie_id doit être NULL
            if plan_data.compagnie_id is not None:
                raise ValueError("Le champ 'compagnie_id' ne doit pas être spécifié lorsqu'aucun 'parent_id' n'est fourni.")

        # Mettre à jour les champs
        update_data = plan_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)

        with transaction(self.db) as session:
            session.commit()
            session.refresh(plan)

        return PlanComptableResponse.from_orm(plan)

    def delete_plan_comptable(self, plan_id: UUID) -> bool:
        """Supprimer (soft delete) un compte"""
        plan = self.get_by_id(plan_id)
        if plan:
            return self.soft_delete(plan_id)
        return False

    def get_all_plans_comptables(self, skip: int = 0, limit: int = 100) -> List[PlanComptableResponse]:
        """Récupérer tous les comptes avec pagination"""
        plans = self.get_all(skip=skip, limit=limit)
        return [PlanComptableResponse.from_orm(plan) for plan in plans]

    def get_plan_hierarchy(self, plan_id: UUID) -> Optional[PlanComptableResponse]:
        """Récupérer un compte avec sa hiérarchie complète"""
        plan = self.db.query(PlanComptableModel).filter(PlanComptableModel.id == plan_id).first()
        if plan:
            return self._build_hierarchy(plan)
        return None

    def get_full_plan_hierarchy(self, compagnie_id: Optional[UUID] = None) -> List[PlanComptableResponse]:
        """Récupérer la hiérarchie complète du plan comptable"""
        # Récupérer tous les comptes racines (sans parent)
        root_plans = self.db.query(PlanComptableModel).filter(PlanComptableModel.parent_id.is_(None)).all()

        if compagnie_id:
            # Filtrer les plans comptables enfants par compagnie_id si spécifié
            return [self._build_hierarchy_filtered(plan, compagnie_id) for plan in root_plans]
        else:
            return [self._build_hierarchy(plan) for plan in root_plans]

    def get_plan_hierarchy_by_numero(self, numero_compte: str, compagnie_id: UUID) -> Optional[PlanComptableResponse]:
        """Récupérer un compte avec sa hiérarchie complète par son numéro de compte"""
        # Récupérer le compte par son numéro
        plan = self.db.query(PlanComptableModel).filter(
            PlanComptableModel.numero_compte == numero_compte,
            # Filtrer par compagnie_id pour les comptes de base (parent_id IS NULL)
            # ou les comptes appartenant à la même compagnie
            or_(
                PlanComptableModel.compagnie_id == compagnie_id,
                PlanComptableModel.parent_id.is_(None)  # Comptes de base
            )
        ).first()

        if plan:
            return self._build_hierarchy_filtered(plan, compagnie_id)
        return None

    def _build_hierarchy(self, plan: PlanComptableModel) -> PlanComptableResponse:
        """Construire récursivement la hiérarchie d'un compte"""
        from ...plan_comptable.schemas import PlanComptableHierarchyResponse

        # Récupérer les enfants directs
        children = self.db.query(PlanComptableModel).filter(PlanComptableModel.parent_id == plan.id).all()

        # Construire l'objet de réponse avec la hiérarchie
        hierarchy_response = PlanComptableHierarchyResponse(
            id=plan.id,
            numero_compte=plan.numero_compte,
            libelle_compte=plan.libelle_compte,
            categorie=plan.categorie,
            type_compte=plan.type_compte,
            parent_id=plan.parent_id,
            compagnie_id=plan.compagnie_id,
            est_actif=plan.est_actif,
            enfants=[self._build_hierarchy(child) for child in children]
        )

        return hierarchy_response

    def _build_hierarchy_filtered(self, plan: PlanComptableModel, compagnie_id: UUID) -> PlanComptableResponse:
        """Construire récursivement la hiérarchie d'un compte en filtrant par compagnie_id"""
        from ...plan_comptable.schemas import PlanComptableHierarchyResponse

        # Récupérer les enfants directs filtrés par compagnie_id
        children = self.db.query(PlanComptableModel).filter(
            PlanComptableModel.parent_id == plan.id,
            # Filtrer les enfants par compagnie_id
            or_(
                PlanComptableModel.compagnie_id == compagnie_id,
                PlanComptableModel.compagnie_id.is_(None)  # Comptes de base
            )
        ).all()

        # Construire l'objet de réponse avec la hiérarchie filtrée
        hierarchy_response = PlanComptableHierarchyResponse(
            id=plan.id,
            numero_compte=plan.numero_compte,
            libelle_compte=plan.libelle_compte,
            categorie=plan.categorie,
            type_compte=plan.type_compte,
            parent_id=plan.parent_id,
            compagnie_id=plan.compagnie_id,
            est_actif=plan.est_actif,
            enfants=[self._build_hierarchy_filtered(child, compagnie_id) for child in children]
        )

        return hierarchy_response