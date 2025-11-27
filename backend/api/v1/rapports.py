from fastapi import APIRouter

router = APIRouter(
    tags=["rapports"],
    responses={404: {"description": "Endpoint non trouvé"}}
)