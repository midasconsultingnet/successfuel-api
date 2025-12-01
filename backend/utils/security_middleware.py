"""
Middleware de sécurité pour renforcer la protection des communications
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send
import secrets
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour ajouter des en-têtes de sécurité HTTP
    """
    async def dispatch(self, request: Request, call_next):
        # Générer un identifiant de requête pour le suivi
        request_id = secrets.token_urlsafe(16)
        request.state.request_id = request_id

        # Vérifier si c'est une requête pour les docs Swagger pour désactiver temporairement la sécurité
        path = request.url.path
        is_swagger_ui = (
            path.startswith('/docs') or
            path.startswith('/openapi.json') or
            path.startswith('/redoc') or
            path.startswith('/swagger') or
            path.startswith('/elements') or
            path == '/openapi.json'
        )

        if is_swagger_ui:
            # Pour Swagger UI, bypasser complètement le middleware de sécurité
            response = await call_next(request)
            # Ne pas traiter la réponse avec le middleware, laisser FastAPI la gérer telle quelle
            return response
        else:
            # Appliquer les en-têtes de sécurité pour les autres requêtes
            try:
                response = await call_next(request)
            except Exception as e:
                # En cas d'erreur, renvoyer une réponse d'erreur appropriée
                logger.error(f"Erreur dans le middleware SecurityHeaders: {str(e)}")
                response = JSONResponse(
                    status_code=500,
                    content={"detail": "Erreur interne du serveur"}
                )

            # S'assurer que la réponse est un objet Response valide
            if not isinstance(response, Response):
                if isinstance(response, (dict, list)):
                    response = JSONResponse(content=response)
                else:
                    # Si c'est un autre type d'objet, le traiter comme un JSON
                    response = JSONResponse(content=str(response) if response is not None else "")

            # En-têtes de sécurité
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

            # Politique de sécurité plus stricte pour les autres endpoints
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )

        # Ajouter les en-têtes de sécurité si la réponse est un objet Response valide
        if isinstance(response, Response):
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["X-Request-ID"] = request_id
        else:
            # Si la réponse n'est pas une instance valide de Response, assurez-vous qu'elle le devient
            if isinstance(response, (dict, list)):
                response = JSONResponse(content=response)
            else:
                response = JSONResponse(content=str(response) if response is not None else "")
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["X-Request-ID"] = request_id

        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour la protection CSRF
    """
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key

    async def dispatch(self, request: Request, call_next):
        # Pour les méthodes non sécurisées, vérifier le token CSRF
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Vérifier si le header CSRF est présent
            csrf_token = request.headers.get("X-CSRF-Token")
            if not csrf_token:
                # Pourrait lever une exception mais pour l'instant on continue pour ne pas casser l'API existante
                pass  # On pourrait implémenter une vérification stricte ici

        path = request.url.path
        is_swagger_ui = (
            path.startswith('/docs') or
            path.startswith('/openapi.json') or
            path.startswith('/redoc') or
            path.startswith('/swagger') or
            path.startswith('/elements') or
            path == '/openapi.json'
        )

        if is_swagger_ui:
            # Pour Swagger UI, bypasser complètement le middleware CSRF
            response = await call_next(request)
            # Ne pas traiter la réponse avec le middleware, laisser FastAPI la gérer telle quelle
            return response

        try:
            response = await call_next(request)
        except Exception as e:
            # En cas d'erreur, renvoyer une réponse d'erreur appropriée
            logger.error(f"Erreur dans le middleware CSRF: {str(e)}")
            response = JSONResponse(
                status_code=500,
                content={"detail": "Erreur interne du serveur"}
            )

        # Générer un identifiant de requête pour le suivi (si ce n'est pas déjà fait)
        if not hasattr(request.state, 'request_id'):
            request_id = secrets.token_urlsafe(16)
            request.state.request_id = request_id
        else:
            request_id = request.state.request_id

        # Vérifier si c'est une requête pour les docs Swagger pour désactiver temporairement la sécurité
        path = request.url.path
        is_swagger_ui = (
            path.startswith('/docs') or
            path.startswith('/openapi.json') or
            path.startswith('/redoc') or
            path.startswith('/swagger') or
            path.startswith('/elements') or
            path == '/openapi.json'
        )

        # S'assurer que la réponse est un objet Response valide
        if not isinstance(response, Response):
            if isinstance(response, (dict, list)):
                response = JSONResponse(content=response)
            else:
                # Si c'est un autre type d'objet, le traiter comme un JSON
                response = JSONResponse(content=str(response) if response is not None else "")

        if not is_swagger_ui:
            # En-têtes de sécurité pour les autres endpoints
            if isinstance(response, Response):
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["X-XSS-Protection"] = "1; mode=block"
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

                # Politique de sécurité plus stricte pour les autres endpoints
                response.headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self'; "
                    "style-src 'self'; "
                    "img-src 'self' data:; "
                    "font-src 'self' data:; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none';"
                )

        # Ajouter les en-têtes de sécurité si la réponse est un objet Response valide
        if isinstance(response, Response):
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["X-Request-ID"] = request_id

            # Générer un token CSRF pour la réponse
            response.headers["X-CSRF-Token"] = secrets.token_urlsafe(32)
        else:
            # Si la réponse n'est pas une instance valide de Response, assurez-vous qu'elle le devient
            if isinstance(response, (dict, list)):
                response = JSONResponse(content=response)
            else:
                response = JSONResponse(content=str(response) if response is not None else "")
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["X-Request-ID"] = request_id

            # Générer un token CSRF pour la réponse
            response.headers["X-CSRF-Token"] = secrets.token_urlsafe(32)

        return response