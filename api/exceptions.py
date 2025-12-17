from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Exception personnalisée pour les ressources non trouvées
    """
    def __init__(self, detail: str = "Ressource non trouvée"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ValidationException(HTTPException):
    """
    Exception personnalisée pour les erreurs de validation
    """
    def __init__(self, detail: str = "Erreur de validation"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )