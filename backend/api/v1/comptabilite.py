from fastapi import APIRouter
from .plan_comptable import router as plan_comptable_router
from .ecritures_comptables import router as ecritures_comptables_router
from .bilan_initial import router as bilan_initial_router
from .rapports import router as rapports_router
from .validation import router as validation_router
from .soldes import router as soldes_router

router = APIRouter(
    tags=["comptabilite"],
    responses={404: {"description": "Endpoint non trouvé"}}
)

# Include all accounting sub-routers
router.include_router(plan_comptable_router, prefix="/plan-comptable", tags=["Plan Comptable"])
router.include_router(ecritures_comptables_router, prefix="/ecritures", tags=["Écritures Comptables"])
router.include_router(bilan_initial_router, prefix="/bilan-initial", tags=["Bilan Initial"])
router.include_router(rapports_router, prefix="/rapports", tags=["Rapports"])
router.include_router(validation_router, prefix="/validation", tags=["Validation"])
router.include_router(soldes_router, prefix="/soldes", tags=["Soldes"])