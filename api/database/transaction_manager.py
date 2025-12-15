from contextlib import contextmanager
from sqlalchemy.orm import Session
from typing import Callable, Any


class TransactionManager:
    """
    Gestionnaire de transactions pour les opérations de base de données.
    """

    @staticmethod
    @contextmanager
    def transaction(session: Session):
        """
        Context manager pour gérer les transactions de base de données.
        """
        transaction = session.begin()
        try:
            yield session
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def execute_in_transaction(
        db: Session,
        operation: Callable[[Session], Any]
    ) -> Any:
        """
        Exécute une opération dans une transaction.

        Args:
            db: Session de base de données
            operation: Fonction à exécuter dans la transaction

        Returns:
            Résultat de l'opération
        """
        # Sauvegarder la session originale pour ne pas la fermer
        original_session = db
        
        try:
            with TransactionManager.transaction(db) as session:
                return operation(session)
        except Exception as e:
            # Ré-émettre l'exception sans fermer la session originale
            raise e


# Alias pour plus de commodité
transaction = TransactionManager.transaction