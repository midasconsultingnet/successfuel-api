from fastapi import APIRouter

router = APIRouter(
    tags=["stocks"],
    responses={404: {"description": "Endpoint non trouvé"}}
)