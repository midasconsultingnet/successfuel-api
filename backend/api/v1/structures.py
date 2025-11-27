from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.database import get_db
from models.structures import Pays, Compagnie, Station, Utilisateur
from services.structures_service import (
    create_pays, get_pays_by_id, get_pays_by_code, get_all_pays, update_pays,
    create_compagnie, get_compagnie_by_id, get_compagnie_by_code, get_all_compagnies, update_compagnie,
    create_station, get_station_by_id, get_station_by_code, get_all_stations, update_station
)
from services.auth_service import get_user_by_id
from utils.security import verify_token
from utils.dependencies import get_current_user
from utils.access_control import require_permission
from pydantic import BaseModel


# Create API router
router = APIRouter(
    tags=["structures"],
    responses={404: {"description": "Endpoint non trouvé"}}
)


# Request/response models
class PaysBase(BaseModel):
    code_pays: str
    nom_pays: str
    devise_principale: str = "MGA"
    taux_tva_par_defaut: float = 20.00
    systeme_comptable: str = "IFRS"
    date_application_tva: Optional[str] = None
    statut: str = "Actif"


class PaysCreate(PaysBase):
    pass


class PaysUpdate(BaseModel):
    nom_pays: Optional[str] = None
    devise_principale: Optional[str] = None
    taux_tva_par_defaut: Optional[float] = None
    systeme_comptable: Optional[str] = None
    date_application_tva: Optional[str] = None
    statut: Optional[str] = None


class PaysResponse(BaseModel):
    id: str
    code_pays: str
    nom_pays: str
    devise_principale: str
    taux_tva_par_defaut: float
    systeme_comptable: str
    date_application_tva: Optional[str] = None
    statut: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class CompagnieBase(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    pays_id: Optional[str] = None
    devise_principale: str = "MGA"


class CompagnieCreate(CompagnieBase):
    pass


class CompagnieUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    pays_id: Optional[str] = None
    devise_principale: Optional[str] = None
    statut: Optional[str] = None


class CompagnieResponse(BaseModel):
    id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    statut: str
    pays_id: Optional[str] = None
    devise_principale: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class StationBase(BaseModel):
    compagnie_id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pays_id: Optional[str] = None


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    compagnie_id: Optional[str] = None
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pays_id: Optional[str] = None
    statut: Optional[str] = None


class StationResponse(BaseModel):
    id: str
    compagnie_id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pays_id: Optional[str] = None
    statut: str
    created_at: str

    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    total: int
    limit: int
    offset: int


class PaysListResponse(BaseModel):
    success: bool
    data: List[PaysResponse]
    pagination: PaginationResponse


class CompagnieListResponse(BaseModel):
    success: bool
    data: List[CompagnieResponse]
    pagination: PaginationResponse


class StationListResponse(BaseModel):
    success: bool
    data: List[StationResponse]
    pagination: PaginationResponse




@router.post("/pays", response_model=PaysResponse)
@require_permission("pays.creer")
async def create_pays_endpoint(
    pays_data: PaysCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new country
    """
    try:
        db_pays = create_pays(
            db,
            code_pays=pays_data.code_pays,
            nom_pays=pays_data.nom_pays,
            devise_principale=pays_data.devise_principale,
            taux_tva_par_defaut=pays_data.taux_tva_par_defaut,
            systeme_comptable=pays_data.systeme_comptable,
            date_application_tva=pays_data.date_application_tva,
            statut=pays_data.statut
        )
        
        return PaysResponse(
            id=str(db_pays.id),
            code_pays=db_pays.code_pays,
            nom_pays=db_pays.nom_pays,
            devise_principale=db_pays.devise_principale,
            taux_tva_par_defaut=float(db_pays.taux_tva_par_defaut),
            systeme_comptable=db_pays.systeme_comptable,
            date_application_tva=db_pays.date_application_tva.isoformat() if db_pays.date_application_tva else None,
            statut=db_pays.statut,
            created_at=db_pays.created_at.isoformat(),
            updated_at=db_pays.updated_at.isoformat() if db_pays.updated_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/pays", response_model=PaysListResponse)
@require_permission("pays.lire")
async def get_pays_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in country name"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all countries with optional filters
    """
    # Only admin users can access countries (countries are not company-specific)
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to countries information is restricted to admin users"
        )

    pays_list = get_all_pays(db, statut=statut, search=search)
    total = len(pays_list)

    # Apply pagination to the results
    paginated_pays = pays_list[offset:offset+limit]

    return PaysListResponse(
        success=True,
        data=[
            PaysResponse(
                id=str(pays.id),
                code_pays=pays.code_pays,
                nom_pays=pays.nom_pays,
                devise_principale=pays.devise_principale,
                taux_tva_par_defaut=float(pays.taux_tva_par_defaut),
                systeme_comptable=pays.systeme_comptable,
                date_application_tva=pays.date_application_tva.isoformat() if pays.date_application_tva else None,
                statut=pays.statut,
                created_at=pays.created_at.isoformat(),
                updated_at=pays.updated_at.isoformat() if pays.updated_at else None
            )
            for pays in paginated_pays
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.put("/pays/{pays_id}", response_model=PaysResponse)
@require_permission("pays.modifier")
async def update_pays_endpoint(
    pays_id: str,
    pays_data: PaysUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a country
    """
    from datetime import datetime

    # Prepare data with proper date conversion
    update_data = pays_data.dict(exclude_unset=True)

    # Convert date_application_tva to proper date format if provided and not None
    if 'date_application_tva' in update_data:
        if update_data['date_application_tva'] is not None:
            try:
                # Try to parse the date string to ensure it's in a valid format
                if isinstance(update_data['date_application_tva'], str):
                    # Parse ISO format date (YYYY-MM-DD)
                    update_data['date_application_tva'] = datetime.strptime(update_data['date_application_tva'], "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format for date_application_tva. Expected format: YYYY-MM-DD"
                )
        # If the value is None, it's already handled correctly by SQLAlchemy

    updated_pays = update_pays(db, pays_id, **update_data)
    if not updated_pays:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )

    return PaysResponse(
        id=str(updated_pays.id),
        code_pays=updated_pays.code_pays,
        nom_pays=updated_pays.nom_pays,
        devise_principale=updated_pays.devise_principale,
        taux_tva_par_defaut=float(updated_pays.taux_tva_par_defaut),
        systeme_comptable=updated_pays.systeme_comptable,
        date_application_tva=updated_pays.date_application_tva.isoformat() if updated_pays.date_application_tva else None,
        statut=updated_pays.statut,
        created_at=updated_pays.created_at.isoformat(),
        updated_at=updated_pays.updated_at.isoformat() if updated_pays.updated_at else None
    )


@router.post("/companies", response_model=CompagnieResponse)
@require_permission("compagnies.creer")
async def create_compagnie_endpoint(
    compagnie_data: CompagnieCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new company
    """
    try:
        db_compagnie = create_compagnie(
            db,
            code=compagnie_data.code,
            nom=compagnie_data.nom,
            adresse=compagnie_data.adresse,
            telephone=compagnie_data.telephone,
            email=compagnie_data.email,
            nif=compagnie_data.nif,
            pays_id=compagnie_data.pays_id,
            devise_principale=compagnie_data.devise_principale
        )
        
        return CompagnieResponse(
            id=str(db_compagnie.id),
            code=db_compagnie.code,
            nom=db_compagnie.nom,
            adresse=db_compagnie.adresse,
            telephone=db_compagnie.telephone,
            email=db_compagnie.email,
            nif=db_compagnie.nif,
            statut=db_compagnie.statut,
            pays_id=str(db_compagnie.pays_id) if db_compagnie.pays_id else None,
            devise_principale=db_compagnie.devise_principale,
            created_at=db_compagnie.created_at.isoformat(),
            updated_at=db_compagnie.updated_at.isoformat() if db_compagnie.updated_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/companies", response_model=CompagnieListResponse)
@require_permission("compagnies.lire")
async def get_compagnies_list(
    statut: Optional[str] = Query(None, description="Filter by status"),
    pays_id: Optional[str] = Query(None, description="Filter by country ID"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all companies with optional filters
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur

    # Only admin users can see all companies
    if is_admin_or_super_admin(user_type):
        # Admins can see all companies with optional filters
        compagnies_list = get_all_compagnies(db, statut=statut, pays_id=pays_id)
    else:
        # Non-admin users can only see their own company
        if current_user.compagnie_id:
            # Fetch only the user's company
            company = get_compagnie_by_id(db, str(current_user.compagnie_id))
            compagnies_list = [company] if company else []
        else:
            compagnies_list = []

    total = len(compagnies_list)

    # Apply pagination to the results
    paginated_compagnies = compagnies_list[offset:offset+limit]

    return CompagnieListResponse(
        success=True,
        data=[
            CompagnieResponse(
                id=str(compagnie.id),
                code=compagnie.code,
                nom=compagnie.nom,
                adresse=compagnie.adresse,
                telephone=compagnie.telephone,
                email=compagnie.email,
                nif=compagnie.nif,
                statut=compagnie.statut,
                pays_id=str(compagnie.pays_id) if compagnie.pays_id else None,
                devise_principale=compagnie.devise_principale,
                created_at=compagnie.created_at.isoformat(),
                updated_at=compagnie.updated_at.isoformat() if compagnie.updated_at else None
            )
            for compagnie in paginated_compagnies
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.put("/companies/{compagnie_id}", response_model=CompagnieResponse)
@require_permission("compagnies.modifier")
async def update_compagnie_endpoint(
    compagnie_id: str,
    compagnie_data: CompagnieUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a company
    """
    updated_compagnie = update_compagnie(db, compagnie_id, **compagnie_data.dict(exclude_unset=True))
    if not updated_compagnie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompagnieResponse(
        id=str(updated_compagnie.id),
        code=updated_compagnie.code,
        nom=updated_compagnie.nom,
        adresse=updated_compagnie.adresse,
        telephone=updated_compagnie.telephone,
        email=updated_compagnie.email,
        nif=updated_compagnie.nif,
        statut=updated_compagnie.statut,
        pays_id=str(updated_compagnie.pays_id) if updated_compagnie.pays_id else None,
        devise_principale=updated_compagnie.devise_principale,
        created_at=updated_compagnie.created_at.isoformat(),
        updated_at=updated_compagnie.updated_at.isoformat() if updated_compagnie.updated_at else None
    )


@router.post("/stations", response_model=StationResponse)
async def create_station_endpoint(
    station_data: StationCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new station
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "creer_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'creer_stations' required"
        )

    # Verify that non-admin users can only create stations for their own company
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # Using str() to ensure both values are properly compared as strings
        user_compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        request_compagnie_id = str(station_data.compagnie_id) if station_data.compagnie_id else None

        if request_compagnie_id != user_compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create stations for your own company"
            )

    try:
        db_station = create_station(
            db,
            compagnie_id=station_data.compagnie_id,
            code=station_data.code,
            nom=station_data.nom,
            adresse=station_data.adresse,
            telephone=station_data.telephone,
            email=station_data.email,
            pays_id=station_data.pays_id
        )
        
        return StationResponse(
            id=str(db_station.id),
            compagnie_id=str(db_station.compagnie_id),
            code=db_station.code,
            nom=db_station.nom,
            adresse=db_station.adresse,
            telephone=db_station.telephone,
            email=db_station.email,
            pays_id=str(db_station.pays_id) if db_station.pays_id else None,
            statut=db_station.statut,
            created_at=db_station.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/stations/{station_id}", response_model=StationResponse)
async def get_station_endpoint(
    station_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get station details by ID
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "lire_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'lire_stations' required"
        )

    station = get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    # Verify that non-admin users can only access stations for their own company
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # Using str() to ensure both values are properly compared as strings
        user_compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        station_compagnie_id = str(station.compagnie_id) if station.compagnie_id else None

        if station_compagnie_id != user_compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access stations for your own company"
            )

    return StationResponse(
        id=str(station.id),
        compagnie_id=str(station.compagnie_id),
        code=station.code,
        nom=station.nom,
        adresse=station.adresse,
        telephone=station.telephone,
        email=station.email,
        pays_id=str(station.pays_id) if station.pays_id else None,
        statut=station.statut,
        created_at=station.created_at.isoformat()
    )


@router.get("/stations", response_model=StationListResponse)
async def get_stations_list(
    compagnie_id: Optional[str] = Query(None, description="Filter by company ID"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    pays_id: Optional[str] = Query(None, description="Filter by country ID"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all stations with optional filters
    """
    from utils.access_control import is_admin_or_super_admin, has_permission

    # Check if the user has the required permission
    if not has_permission(db, str(current_user.id), "lire_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'lire_stations' required"
        )

    # Non-admin users can only see stations from their own company
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # For non-admin users, only show stations from their company
        # Check if requested company ID matches user's company (if provided)
        if compagnie_id and compagnie_id != str(current_user.compagnie_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access stations for your own company"
            )
        user_compagnie_id = current_user.compagnie_id
        stations_list = get_all_stations(
            db,
            compagnie_id=user_compagnie_id,  # Override any provided compagnie_id filter
            statut=statut,
            pays_id=pays_id
        )
    else:
        # Admin users can see all stations or filtered by compagnie_id if provided
        stations_list = get_all_stations(
            db,
            compagnie_id=compagnie_id,
            statut=statut,
            pays_id=pays_id
        )

    total = len(stations_list)

    # Apply pagination to the results
    paginated_stations = stations_list[offset:offset+limit]

    return StationListResponse(
        success=True,
        data=[
            StationResponse(
                id=str(station.id),
                compagnie_id=str(station.compagnie_id),
                code=station.code,
                nom=station.nom,
                adresse=station.adresse,
                telephone=station.telephone,
                email=station.email,
                pays_id=str(station.pays_id) if station.pays_id else None,
                statut=station.statut,
                created_at=station.created_at.isoformat()
            )
            for station in paginated_stations
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.put("/stations/{station_id}", response_model=StationResponse)
async def update_station_endpoint(
    station_id: str,
    station_data: StationUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a station
    """
    from utils.access_control import is_admin_or_super_admin
    from services.rbac_service import check_user_permission

    # Check if the user has the required permission
    if not check_user_permission(db, str(current_user.id), "modifier_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'modifier_stations' required"
        )

    # Get the station to check if it belongs to the user's company
    station = get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    # Verify that non-admin users can only update stations for their own company
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # Using str() to ensure both values are properly compared as strings
        user_compagnie_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        station_compagnie_id = str(station.compagnie_id) if station.compagnie_id else None

        if station_compagnie_id != user_compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update stations for your own company"
            )

    updated_station = update_station(db, station_id, **station_data.dict(exclude_unset=True))
    if not updated_station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    return StationResponse(
        id=str(updated_station.id),
        compagnie_id=str(updated_station.compagnie_id),
        code=updated_station.code,
        nom=updated_station.nom,
        adresse=updated_station.adresse,
        telephone=updated_station.telephone,
        email=updated_station.email,
        pays_id=str(updated_station.pays_id) if updated_station.pays_id else None,
        statut=updated_station.statut,
        created_at=updated_station.created_at.isoformat()
    )