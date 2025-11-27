from fastapi import APIRouter

router = APIRouter(
    tags=["comptabilite"],
    responses={404: {"description": "Endpoint non trouvé"}}
)