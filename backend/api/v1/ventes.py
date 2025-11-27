from fastapi import APIRouter

router = APIRouter(
    tags=["ventes"],
    responses={404: {"description": "Endpoint non trouvé"}}
)