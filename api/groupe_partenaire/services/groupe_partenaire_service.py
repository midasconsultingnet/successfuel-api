from sqlalchemy.orm import Session
from typing import List, Optional
from ...models.groupe_partenaire import GroupePartenaire
from ...services.database_service import DatabaseService
from ..schemas import GroupePartenaireCreate, GroupePartenaireUpdate


class GroupePartenaireService:
    def __init__(self):
        self.model_class = GroupePartenaire

    def create_groupe_partenaire(self, db: Session, groupe_data: GroupePartenaireCreate) -> GroupePartenaire:
        """
        Crée un nouveau groupe partenaire
        """
        db_service = DatabaseService(db, self.model_class)
        return db_service.create(groupe_data.dict())

    def get_groupe_partenaire(self, db: Session, groupe_id: str) -> Optional[GroupePartenaire]:
        """
        Récupère un groupe partenaire par son ID
        """
        db_service = DatabaseService(db, self.model_class)
        return db_service.get_by_id(groupe_id)

    def get_groupes_partenaire(self, db: Session, skip: int = 0, limit: int = 100) -> List[GroupePartenaire]:
        """
        Récupère une liste de groupes partenaires avec pagination
        """
        db_service = DatabaseService(db, self.model_class)
        return db_service.get_all(skip=skip, limit=limit)

    def update_groupe_partenaire(self, db: Session, groupe_id: str, groupe_data: GroupePartenaireUpdate) -> Optional[GroupePartenaire]:
        """
        Met à jour un groupe partenaire existant
        """
        update_data = groupe_data.dict(exclude_unset=True)
        db_service = DatabaseService(db, self.model_class)
        return db_service.update(groupe_id, update_data)

    def delete_groupe_partenaire(self, db: Session, groupe_id: str) -> bool:
        """
        Supprime un groupe partenaire (soft delete)
        """
        db_service = DatabaseService(db, self.model_class)
        return db_service.delete(groupe_id)