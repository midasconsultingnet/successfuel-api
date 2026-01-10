from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging


# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseIntegrityException(Exception):
    """
    Exception personnalisée pour les erreurs d'intégrité de base de données
    """
    def __init__(self, message: str = "Erreur d'intégrité de la base de données"):
        self.message = message
        super().__init__(self.message)


async def database_integrity_exception_handler(request: Request, exc: DatabaseIntegrityException):
    """Gestion des erreurs d'intégrité de base de données personnalisées"""
    logger.error(f"Erreur d'intégrité de base de données: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc.orig) if hasattr(exc, 'orig') else str(exc)}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gestion des erreurs de validation Pydantic"""
    logger.error(f"Erreur de validation: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": "Erreurs de validation",
            "errors": exc.errors()
        })
    )


async def database_integrity_exception_handler_old(request: Request, exc: IntegrityError):
    """Gestion des erreurs d'intégrité de base de données"""
    logger.error(f"Erreur d'intégrité de base de données: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Erreur d'intégrité de la base de données"}
    )


async def database_sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Gestion des erreurs SQLAlchemy génériques"""
    logger.error(f"Erreur SQLAlchemy: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Erreur de base de données"}
    )


def convert_uuid_to_str(obj):
    """Convertit récursivement les objets UUID en chaînes dans un objet imbriqué"""
    if isinstance(obj, dict):
        return {key: convert_uuid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuid_to_str(item) for item in obj]
    elif isinstance(obj, type(__import__('uuid').UUID)):
        return str(obj)
    else:
        return obj


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Gestion des erreurs de validation Pydantic"""
    errors = convert_uuid_to_str(exc.errors())
    logger.error(f"Erreur de validation Pydantic: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Erreurs de validation Pydantic", "errors": errors}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Gestion des erreurs générales"""
    error_msg = str(exc)
    logger.error(f"Erreur non gérée: {error_msg}")

    # Vérifier si l'erreur contient des objets non sérialisables
    try:
        # Essayer de créer la réponse normalement
        response_content = {"detail": "Erreur interne du serveur"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_content
        )
    except TypeError as e:
        # Si une erreur de sérialisation se produit, renvoyer un message générique
        logger.error(f"Erreur de sérialisation dans le gestionnaire d'erreurs: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Erreur interne du serveur - problème de sérialisation"}
        )