from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI
import os

# Création du rate limiter
limiter = Limiter(key_func=get_remote_address)

def add_rate_limiter(app: FastAPI):
    """Ajoute le gestionnaire de rate limiting à l'application FastAPI"""
    # Désactiver le rate limiting en développement
    if os.getenv("ENVIRONMENT") == "development":
        # En développement, désactiver le rate limiting
        app.state.limiter = None
    else:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Définition des limites spécifiques
# Limite de 5 requêtes par minute pour les endpoints d'authentification
auth_limiter = "5/minute"

# Limite de 100 requêtes par minute pour les autres endpoints
default_limiter = "100/minute"

# Pour les endpoints de création/modification, utiliser une limite plus stricte
write_limiter = "50/minute"

def get_limit_for_env(limit_str: str):
    """Retourne la limite appropriée selon l'environnement"""
    if os.getenv("ENVIRONMENT") == "development":
        return "1000/minute"  # Très haute limite en développement
    return limit_str