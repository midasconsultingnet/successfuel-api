from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..database import get_db
from ..models.carburant import Carburant
from ..models.compagnie import Compagnie, Station, Cuve
from .schemas import CarburantResponse, CarburantGroupedByCompany
from ..auth.auth_handler import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.get("/carburants", response_model=List[CarburantResponse])
async def get_carburants(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Retrieve list of all carburants
    """
    current_user = get_current_user(db, credentials.credentials)

    carburants = db.query(Carburant).all()
    return carburants


@router.get("/carburants/grouped-by-company", response_model=List[CarburantGroupedByCompany])
async def get_carburants_grouped_by_company(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Retrieve list of carburants grouped by company
    """
    current_user = get_current_user(db, credentials.credentials)

    # Join carburant with cuve and then with station to get the associated companies
    # Since carburant is connected to cuve, and cuve is connected to station, and station to compagnie
    results = (
        db.query(Carburant, Compagnie)
        .join(Cuve, Cuve.carburant_id == Carburant.id)
        .join(Station, Station.id == Cuve.station_id)  # Join with station
        .join(Compagnie, Compagnie.id == Station.compagnie_id)  # Then with compagnie
        .distinct(Carburant.id, Compagnie.id)
        .all()
    )

    # Group the results by company
    grouped_data = {}
    for carburant, compagnie in results:
        if compagnie.id not in grouped_data:
            grouped_data[compagnie.id] = {
                "compagnie_id": compagnie.id,
                "compagnie_nom": compagnie.nom,
                "carburants": []
            }

        # Check if the carburant is already in the list to avoid duplicates
        if not any(c.id == carburant.id for c in grouped_data[compagnie.id]["carburants"]):
            grouped_data[compagnie.id]["carburants"].append(carburant)

    # Convert the grouped data to the required format
    response_data = [
        CarburantGroupedByCompany(**data)
        for data in grouped_data.values()
    ]

    return response_data