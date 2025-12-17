from sqlalchemy.orm import Session
from typing import Callable, Any
from ..database.transaction_manager import transaction, TransactionManager
from ..exception_handlers import DatabaseIntegrityException
from ..models.user import User
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Service de base pour les opérations liées à la base de données.
    Fournit des méthodes utilitaires pour la gestion des entités avec
    des transactions et la gestion des erreurs.
    """

    @staticmethod
    def create_with_transaction(
        db: Session,
        model_class,
        **kwargs
    ) -> Any:
        """
        Crée une nouvelle entité dans une transaction.

        Args:
            db: Session de base de données
            model_class: Classe du modèle à créer
            **kwargs: Attributs de l'entité

        Returns:
            L'entité créée
        """
        logger.info(f"Creating new entity of type {model_class.__name__}")
        try:
            with TransactionManager.transaction(db) as session:
                entity = model_class(**kwargs)
                session.add(entity)
                session.flush()  # Pour obtenir l'ID avant le commit
                logger.info(f"Successfully created entity {model_class.__name__} with ID: {getattr(entity, 'id', 'N/A')}")
                return entity
        except Exception as e:
            logger.error(f"Error creating entity of type {model_class.__name__}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def update_with_transaction(
        db: Session,
        model_class,
        entity_id: UUID,
        **kwargs
    ) -> Any:
        """
        Met à jour une entité dans une transaction.

        Args:
            db: Session de base de données
            model_class: Classe du modèle à mettre à jour
            entity_id: ID de l'entité à mettre à jour
            **kwargs: Attributs à mettre à jour

        Returns:
            L'entité mise à jour
        """
        logger.info(f"Updating entity {model_class.__name__} with ID: {entity_id}")
        try:
            with TransactionManager.transaction(db) as session:
                entity = session.query(model_class).filter(
                    model_class.id == entity_id
                ).first()

                if not entity:
                    logger.error(f"{model_class.__name__} avec ID {entity_id} non trouvé")
                    raise ValueError(f"{model_class.__name__} avec ID {entity_id} non trouvé")

                # Mettre à jour les attributs
                for key, value in kwargs.items():
                    setattr(entity, key, value)

                # Mettre à jour la date de modification
                if hasattr(entity, 'update_timestamp'):
                    entity.update_timestamp()

                session.flush()
                logger.info(f"Successfully updated entity {model_class.__name__} with ID: {entity_id}")
                return entity
        except Exception as e:
            logger.error(f"Error updating entity {model_class.__name__} with ID {entity_id}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def delete_with_transaction(
        db: Session,
        model_class,
        entity_id: UUID
    ) -> bool:
        """
        Supprime une entité dans une transaction (soft delete si disponible).

        Args:
            db: Session de base de données
            model_class: Classe du modèle à supprimer
            entity_id: ID de l'entité à supprimer

        Returns:
            True si la suppression a réussi, False sinon
        """
        logger.info(f"Deleting entity {model_class.__name__} with ID: {entity_id}")
        try:
            with TransactionManager.transaction(db) as session:
                entity = session.query(model_class).filter(
                    model_class.id == entity_id
                ).first()

                if not entity:
                    logger.error(f"{model_class.__name__} avec ID {entity_id} non trouvé")
                    raise ValueError(f"{model_class.__name__} avec ID {entity_id} non trouvé")

                # Utiliser le soft delete si la méthode est disponible
                if hasattr(entity, 'soft_delete'):
                    entity.soft_delete()
                else:
                    session.delete(entity)

                session.flush()
                logger.info(f"Successfully deleted entity {model_class.__name__} with ID: {entity_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting entity {model_class.__name__} with ID {entity_id}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def bulk_create_with_transaction(
        db: Session,
        model_class,
        entities_data: list
    ) -> list:
        """
        Crée plusieurs entités dans une transaction.

        Args:
            db: Session de base de données
            model_class: Classe du modèle à créer
            entities_data: Liste des données des entités à créer

        Returns:
            Liste des entités créées
        """
        logger.info(f"Bulk creating {len(entities_data)} entities of type {model_class.__name__}")
        try:
            with TransactionManager.transaction(db) as session:
                entities = []
                for data in entities_data:
                    entity = model_class(**data)
                    session.add(entity)
                    entities.append(entity)

                session.flush()
                logger.info(f"Successfully bulk created {len(entities)} entities of type {model_class.__name__}")
                return entities
        except Exception as e:
            logger.error(f"Error bulk creating entities of type {model_class.__name__}: {str(e)}", exc_info=True)
            raise


# Service spécialisé pour la gestion des utilisateurs
class UserService(DatabaseService):
    """
    Service pour la gestion des utilisateurs avec transactions.
    """
    
    @staticmethod
    def create_user_with_transaction(
        db: Session,
        **user_data
    ) -> User:
        """
        Crée un utilisateur dans une transaction.
        
        Args:
            db: Session de base de données
            **user_data: Données de l'utilisateur
        
        Returns:
            L'utilisateur créé
        """
        return DatabaseService.create_with_transaction(
            db, User, **user_data
        )
    
    @staticmethod
    def update_user_with_transaction(
        db: Session,
        user_id: UUID,
        **user_data
    ) -> User:
        """
        Met à jour un utilisateur dans une transaction.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur à mettre à jour
            **user_data: Données à mettre à jour
        
        Returns:
            L'utilisateur mis à jour
        """
        return DatabaseService.update_with_transaction(
            db, User, user_id, **user_data
        )