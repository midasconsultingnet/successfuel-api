from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1",
    tags=["stocks"],
    responses={404: {"description": "Endpoint non trouvé"}}
)