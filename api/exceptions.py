class InsufficientFundsException(Exception):
    """Exception levée lorsqu'une trésorerie n'a pas suffisamment de fonds pour une transaction."""
    pass


class InvalidTransactionException(Exception):
    """Exception levée lorsqu'une transaction est invalide."""
    pass


class NotFoundException(Exception):
    """Exception levée lorsqu'une ressource n'est pas trouvée."""
    pass


class ValidationException(Exception):
    """Exception levée lorsqu'une validation échoue."""
    pass


class EntityNotFoundException(Exception):
    """Exception levée lorsqu'une entité n'est pas trouvée."""
    pass


class ValidationErrorException(Exception):
    """Exception levée lorsqu'une validation de données échoue."""
    pass


class DatabaseIntegrityException(Exception):
    """Exception levée lorsqu'une contrainte d'intégrité de base de données est violée."""
    pass