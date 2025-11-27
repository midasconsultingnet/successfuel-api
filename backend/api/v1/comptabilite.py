from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1",
    tags=["comptabilite"],
    responses={404: {"description": "Endpoint non trouvé"}}
)