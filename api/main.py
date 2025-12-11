from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import SessionLocal, engine
from . import models

# Initialize the database tables (moved to end to avoid import issues)
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Succès Fuel API",
    description="API for managing fuel station operations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all module routers
def include_routers():
    from .auth.router import router as auth_router
    from .compagnie.router import router as compagnie_router
    from .tiers.router import router as tiers_router
    from .produits.router import router as produits_router
    from .stocks.router import router as stocks_router
    from .achats.router import router as achats_router
    from .achats_carburant.router import router as achats_carburant_router
    from .ventes.router import router as ventes_router
    from .inventaires.router import router as inventaires_router
    from .livraisons.router import router as livraisons_router
    from .tresoreries.router import router as tresoreries_router
    from .mouvements_financiers.router import router as mouvements_financiers_router
    from .salaires.router import router as salaires_router
    from .charges.router import router as charges_router
    from .immobilisations.router import router as immobilisations_router
    from .bilans.router import router as bilans_router
    from .config.router import router as config_router
    from .health.router import router as health_router

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentification"])
    app.include_router(compagnie_router, prefix="/api/v1/compagnie", tags=["compagnie"])
    app.include_router(tiers_router, prefix="/api/v1/tiers", tags=["tiers"])
    app.include_router(produits_router, prefix="/api/v1/produits", tags=["produits"])
    app.include_router(stocks_router, prefix="/api/v1/stocks", tags=["stocks"])
    app.include_router(achats_router, prefix="/api/v1/achats", tags=["achats"])
    app.include_router(achats_carburant_router, prefix="/api/v1/achats-carburant", tags=["achats_carburant"])
    app.include_router(ventes_router, prefix="/api/v1/ventes", tags=["ventes"])
    app.include_router(inventaires_router, prefix="/api/v1/inventaires", tags=["inventaires"])
    app.include_router(livraisons_router, prefix="/api/v1/livraisons", tags=["livraisons"])
    app.include_router(tresoreries_router, prefix="/api/v1/tresoreries", tags=["tresoreries"])
    app.include_router(mouvements_financiers_router, prefix="/api/v1/mouvements-financiers", tags=["mouvements_financiers"])
    app.include_router(salaires_router, prefix="/api/v1/salaires", tags=["salaires"])
    app.include_router(charges_router, prefix="/api/v1/charges", tags=["charges"])
    app.include_router(immobilisations_router, prefix="/api/v1/immobilisations", tags=["immobilisations"])
    app.include_router(bilans_router, prefix="/api/v1/bilans", tags=["bilans"])
    app.include_router(config_router, prefix="/api/v1/config", tags=["configuration"])
    app.include_router(health_router, prefix="/api/v1", tags=["health"])

include_routers()

@app.get("/")
def root():
    return {"message": "Welcome to Succès Fuel API"}