import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.config import settings
from database.database import engine, Base
from api.v1.structures import router as structures_router
from api.v1.auth import router as auth_router
from api.v1.achats import router as achats_router
from api.v1.ventes import router as ventes_router
from api.v1.stocks import router as stocks_router
from api.v1.stocks_updated import router as stocks_updated_router
from api.v1.stocks_initialisation import router as stocks_initialisation_router
from api.v1.tresoreries import router as tresoreries_router
from api.v1.comptabilite import router as comptabilite_router
from api.v1.rapports import router as rapports_router
from api.v1.securite import router as securite_router
from api.v1.rbac import router as rbac_router
from api.v1.security_logs import router as security_logs_router
from api.v1.admin import router as admin_router

# Import de GraphQL
from strawberry.fastapi import GraphQLRouter
from strawberry_graphql.schema import schema
from strawberry_graphql.context import get_context

# Import pour les requêtes SQL
from sqlalchemy import text

# Import des middlewares de sécurité
from utils.security_middleware import SecurityHeadersMiddleware, CSRFMiddleware
# Import du middleware de validation des endpoints
from utils.endpoint_validation import EndpointValidationMiddleware

# Configuration de la journalisation
from utils.logging_config import setup_logging
app_logger, security_logger = setup_logging()
logger = app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code à exécuter au démarrage
    logger.info("Démarrage de l'application SuccessFuel")

    # Création des tables dans la base de données
    Base.metadata.create_all(bind=engine)

    # Test de connexion à la base de données
    try:
        with engine.connect() as connection:
            # Cela va lancer une exception si la connexion échoue
            result = connection.execute(text("SELECT 1"))
            logger.info("Connexion à la base de données réussie")
    except Exception as e:
        logger.error(f"Échec de la connexion à la base de données: {e}")
        # On ne lève pas l'exception pour permettre au serveur de continuer à démarrer

    yield  # Ici, l'application est en cours d'exécution

    # Code à exécuter à l'arrêt
    logger.info("Arrêt de l'application SuccessFuel")
    # Toutes les ressources sont automatiquement gérées maintenant

app = FastAPI(
    title=settings.app_name,
    description="""
    # API SuccessFuel v1.0

    API pour la gestion des stations-service à Madagascar.

    ## Modules disponibles
    - **structures** : Gestion des structures (pays, compagnies, stations)
    - **auth** : Authentification des utilisateurs
    - **achats** : Gestion des achats
    - **ventes** : Gestion des ventes
    - **stocks** : Gestion des stocks
    - **tresoreries** : Gestion de trésorerie
    - **comptabilite** : Gestion comptable
    - **rapports** : Génération de rapports
    - **securite** : Sécurité et gestion des accès
    - **rbac** : Contrôle d'accès basé sur les rôles
    - **security_logs** : Journalisation et surveillance de sécurité
    - **admin** : Fonctionnalités d'administration
    """,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Ajout des middlewares de sécurité
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware, secret_key=settings.secret_key)
app.add_middleware(EndpointValidationMiddleware)

# Configuration du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustez cette liste selon vos besoins de sécurité
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Exposer les en-têtes pour les requêtes GraphQL
    expose_headers=["Access-Control-Allow-Origin"]
)

# Inclusion des routeurs API REST
app.include_router(structures_router, prefix="/api/v1/structures", tags=["structures"])
app.include_router(auth_router, tags=["auth"])  # Pas de préfixe car déjà inclus dans le routeur
app.include_router(achats_router, prefix="/api/v1", tags=["achats"])
app.include_router(ventes_router, prefix="/api/v1", tags=["ventes"])
app.include_router(stocks_router, prefix="/api/v1", tags=["stocks"])
app.include_router(stocks_updated_router, prefix="/api/v1", tags=["stocks_updated"])
# Inclusion du routeur pour les endpoints d'initialisation des stocks
# Le tag "stocks_initialisation" est utilisé comme identifiant technique interne
app.include_router(stocks_initialisation_router, prefix="/api/v1", tags=["stocks_initialisation"])
app.include_router(tresoreries_router, prefix="/api/v1", tags=["tresoreries"])
app.include_router(comptabilite_router, prefix="/api/v1", tags=["comptabilite"])
app.include_router(rapports_router, prefix="/api/v1", tags=["rapports"])
app.include_router(securite_router, prefix="/api/v1", tags=["securite"])
app.include_router(rbac_router, prefix="/api/v1", tags=["rbac"])
app.include_router(security_logs_router, prefix="/api/v1", tags=["security_logs"])
app.include_router(admin_router, tags=["admin"])  # Pas de préfixe car déjà inclus dans le routeur

# Ajout de l'endpoint GraphQL
graphql_app = GraphQLRouter(schema, context_getter=get_context)
# Inclure l'endpoint GraphQL sans l'ajouter au schéma OpenAPI pour éviter les conflits
app.include_router(graphql_app, prefix="/graphql", tags=["graphql"], include_in_schema=False)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "API SuccessFuel v1.0 with FastAPI"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.get("/db-check")
def db_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {"status": "success", "message": "Connected to database"}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return {"status": "error", "message": f"Failed to connect to database: {e}"}

from starlette.responses import JSONResponse

# Gestion globale des erreurs
@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"}
    )

@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    logger.warning(f"Resource not found: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": "Resource not found"}
    )