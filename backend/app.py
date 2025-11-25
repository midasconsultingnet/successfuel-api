import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.config import settings
from database.database import engine, Base
from api.v1.structures import router as structures_router
from api.v1.auth import router as auth_router
from api.v1.achats import router as achats_router
from api.v1.ventes import router as ventes_router
from api.v1.stocks import router as stocks_router
from api.v1.tresoreries import router as tresoreries_router
from api.v1.comptabilite import router as comptabilite_router
from api.v1.rapports import router as rapports_router
from api.v1.securite import router as securite_router

# Import de GraphQL
from strawberry.fastapi import GraphQLRouter
from strawberry_graphql.schema import schema
from strawberry_graphql.context import get_context

# Import pour les requêtes SQL
from sqlalchemy import text

# Configuration de la journalisation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

app = FastAPI(title=settings.app_name, debug=settings.debug)

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
app.include_router(structures_router, prefix="/api/v1", tags=["structures"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(achats_router, prefix="/api/v1", tags=["achats"])
app.include_router(ventes_router, prefix="/api/v1", tags=["ventes"])
app.include_router(stocks_router, prefix="/api/v1", tags=["stocks"])
app.include_router(tresoreries_router, prefix="/api/v1", tags=["tresoreries"])
app.include_router(comptabilite_router, prefix="/api/v1", tags=["comptabilite"])
app.include_router(rapports_router, prefix="/api/v1", tags=["rapports"])
app.include_router(securite_router, prefix="/api/v1", tags=["securite"])

# Ajout de l'endpoint GraphQL
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])

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

# Gestion globale des erreurs
@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return {"status": "error", "message": "Internal server error"}

@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    logger.warning(f"Resource not found: {request.url}")
    return {"status": "error", "message": "Resource not found"}