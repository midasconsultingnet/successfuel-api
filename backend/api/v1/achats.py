from fastapi import APIRouter

router = APIRouter(
    tags=["achats"],
    responses={404: {"description": "Endpoint non trouvé"}}
)