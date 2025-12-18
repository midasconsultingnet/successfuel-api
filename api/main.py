import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
from .translations import get_translation
from .database import SessionLocal, engine
from .exception_handlers import (
    validation_exception_handler,
    database_integrity_exception_handler,
    database_sqlalchemy_exception_handler,
    pydantic_validation_exception_handler,
    general_exception_handler
)
from .services.database_service import DatabaseIntegrityException
from .rate_limiter import add_rate_limiter
from .logging_config import setup_logging

# Importer les modèles pour s'assurer qu'ils sont enregistrés
from .models import Base

# Setup logging system
setup_logging()

# Créer toutes les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# Classe pour le middleware i18n
class I18nMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        accept_language = request.headers.get("accept-language", "fr")
        locale = accept_language.split(",")[0].split("-")[0]

        # S'assurer que la locale est soit 'fr' soit 'en'
        if locale not in ["fr", "en"]:
            locale = "fr"

        # Stocker la langue dans la requête pour utilisation ultérieure
        request.state.lang = locale

        response = await call_next(request)
        return response

# Initialiser l'application
app = FastAPI(
    title="Succès Fuel API",
    description="API for managing fuel station operations",
    version="1.0.0"
)

# Ajouter le middleware i18n
app.add_middleware(I18nMiddleware)

# Ajouter le middleware de rate limiting
# Désactiver le middleware en développement pour éviter les erreurs
if os.getenv("ENVIRONMENT") != "development":
    app.add_middleware(SlowAPIMiddleware)

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter le rate limiter à l'application
add_rate_limiter(app)

# Ajouter les gestionnaires d'exceptions
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, database_integrity_exception_handler)
app.add_exception_handler(DatabaseIntegrityException, database_integrity_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Fonction pour extraire la langue du header Accept-Language
def obtenir_langue_depuis_en_tete(request: Request):
    accept_language = request.headers.get("accept-language", "fr")
    # Extraire la langue principale (ex: "fr" si "fr-FR,en;q=0.9")
    langue = accept_language.split(",")[0].split("-")[0]
    return langue

# Exemple d'exception localisée
class ExceptionLocalisee(HTTPException):
    def __init__(self, code_statut: int, cle_message: str, request: Request):
        # Utiliser les traductions depuis notre nouveau système
        detail = get_translation(cle_message, request.state.lang, "common")
        super().__init__(status_code=code_statut, detail=detail)

# Endpoint racine avec message localisé
@app.get("/")
async def racine(request: Request):
    message = get_translation("welcome_message", request.state.lang, "common")
    return {"message": message}

# Endpoint de test pour bcrypt
@app.get("/test-bcrypt")
async def test_bcrypt():
    try:
        import bcrypt
        import passlib
        from passlib.context import CryptContext

        # Test de la version de bcrypt
        try:
            # Obtenir la version de bcrypt de manière sécurisée
            if hasattr(bcrypt, '__version__'):
                bcrypt_version = bcrypt.__version__
            elif hasattr(bcrypt, '__about__') and hasattr(bcrypt.__about__, '__version__'):
                # Pour les versions récentes de bcrypt qui ont __about__
                bcrypt_version = getattr(bcrypt.__about__, '__version__', 'Version info not available')
            else:
                # Dernier recours : tenter de lire directement la version
                try:
                    import pkg_resources
                    bcrypt_version = pkg_resources.get_distribution("bcrypt").version
                except Exception:
                    bcrypt_version = "Version info not available"
        except Exception:
            bcrypt_version = "Could not retrieve version"

        # Configuration de passlib
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Test de hachage/verification
        test_password = "test_password_123"
        hashed = pwd_context.hash(test_password)
        verified = pwd_context.verify(test_password, hashed)

        # Test avec un mot de passe long
        long_password = "a" * 80  # Plus long que la limite de 72 octets
        try:
            long_hashed = pwd_context.hash(long_password[:72])  # Tronquer à 72 caractères
            long_verified = pwd_context.verify(long_password[:72], long_hashed)
        except ValueError as e:
            return {
                "bcrypt_version": bcrypt_version,
                "passlib_version": passlib.__version__,
                "hash_verification_test": "Success",
                "long_password_test": f"Failed with error: {str(e)}"
            }

        return {
            "bcrypt_version": bcrypt_version,
            "passlib_version": passlib.__version__,
            "hash_verification_test": "Success",
            "verified_correctly": verified,
            "long_password_test": "Success",
            "long_password_verified": long_verified
        }
    except ImportError as e:
        return {"error": f"Import error: {str(e)}"}
    except Exception as e:
        return {"error": f"Bcrypt test failed: {str(e)}"}

# Include all module routers
def inclure_routes():
    from .auth.router import router as auth_router
    from .compagnie.router import router as compagnie_router
    from .tiers.router import router as tiers_router
    from .produits.router import router as produits_router
    from .stocks.router import router as stocks_router
    from .achats.router import router as achats_router
    from .achats.demande_achat_router import router as demande_achat_router
    from .achats_carburant.router import router as achats_carburant_router
    from .achats_carburant.stock_calculation_router import router as stock_calculation_router
    from .ventes.router import router as ventes_router
    from .inventaires.router import router as inventaires_router
    from .livraisons.router import router as livraisons_router
    from .tresoreries.router import router as tresoreries_router
    from .methode_paiement.router import router as methode_paiement_router
    from .mouvements_financiers.router import router as mouvements_financiers_router
    from .salaires.router import router as salaires_router
    from .charges.router import router as charges_router
    from .immobilisations.router import router as immobilisations_router
    from .bilans.router import router as bilans_router
    from .config.router import router as config_router
    from .health.router import router as health_router
    from .carburant.router import router as carburant_router
    from .rbac_router import router as rbac_router
    from .ecritures_comptables.router import router as ecritures_comptables_router

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentification"])
    app.include_router(compagnie_router, prefix="/api/v1/compagnie", tags=["Compagnie"])
    app.include_router(tiers_router, prefix="/api/v1/tiers", tags=["Tiers"])
    app.include_router(tresoreries_router, prefix="/api/v1/tresoreries", tags=["Tresorerie"])
    app.include_router(methode_paiement_router, prefix="/api/v1/methodes-paiement", tags=["Methodes paiement"])
    app.include_router(produits_router, prefix="/api/v1/produits", tags=["Produits"])
    app.include_router(stocks_router, prefix="/api/v1/stocks", tags=["Stock initial"])
    app.include_router(achats_router, prefix="/api/v1/achats", tags=["achats"])
    app.include_router(demande_achat_router, prefix="/api/v1/achats", tags=["achats"])
    app.include_router(achats_carburant_router, prefix="/api/v1/achats-carburant", tags=["Achats carburant"])
    #app.include_router(stock_calculation_router, prefix="/api/v1/achats-carburant", tags=["calculs-stock-carburant"])
    app.include_router(ventes_router, prefix="/api/v1/ventes", tags=["Ventes"])
    app.include_router(inventaires_router, prefix="/api/v1/inventaires", tags=["Inventaires"])
    app.include_router(livraisons_router, prefix="/api/v1/livraisons", tags=["Livraisons"])  
    app.include_router(mouvements_financiers_router, prefix="/api/v1/mouvements-financiers", tags=["Mouvements financiers"])
    app.include_router(salaires_router, prefix="/api/v1/salaires", tags=["Salaires"])
    app.include_router(charges_router, prefix="/api/v1/charges", tags=["Charges"])
    app.include_router(immobilisations_router, prefix="/api/v1/immobilisations", tags=["Immobilisations"])
    app.include_router(bilans_router, prefix="/api/v1/bilans", tags=["Bilans"])
    app.include_router(config_router, prefix="/api/v1/config", tags=["Configurations"])
    app.include_router(health_router, prefix="/api/v1", tags=["systeme"])
    app.include_router(carburant_router, prefix="/api/v1/carburant", tags=["Carburant"])
    app.include_router(rbac_router, prefix="/api/v1/rbac", tags=["rbac"])
    app.include_router(ecritures_comptables_router, prefix="/api/v1/ecritures-comptables", tags=["Ecriture comptable"])

inclure_routes()