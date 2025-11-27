from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1",
    tags=["rapports"],
    responses={404: {"description": "Endpoint non trouvé"}}
)