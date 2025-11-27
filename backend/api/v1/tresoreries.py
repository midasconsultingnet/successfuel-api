from fastapi import APIRouter

router = APIRouter(
    tags=["tresoreries"],
    responses={404: {"description": "Endpoint non trouvé"}}
)