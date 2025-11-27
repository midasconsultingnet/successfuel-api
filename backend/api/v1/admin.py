from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database.database import get_db
from models.structures import Utilisateur, Compagnie, Station, Pays, Profil, Permission
from services.auth_service import get_user_by_id, authenticate_user, log_login_attempt, log_unauthorized_access_attempt, get_user_by_login, create_user, update_user, delete_user, activate_user, deactivate_user, get_all_users
from services.rbac_service import get_all_profils, get_all_permissions, get_all_modules, create_module, create_permission, create_profil, get_permissions_for_profil, assign_permissions_to_profil, update_profil, delete_profil
from utils.security import verify_token
from utils.access_control import is_admin_or_super_admin
from utils.dependencies import get_token_from_header
from typing import List, Optional
from pydantic import BaseModel
import uuid


# Create API router for admin endpoints
router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    responses={404: {"description": "Endpoint non trouvé"}}
)


# Request/response models for auth
class UserLogin(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    data: dict


import logging

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Move the route definition inside a function to catch any errors during definition
def create_login_endpoint():
    @router.post("/login", response_model=LoginResponse)
    async def login_for_admin_access_token(
        user_credentials: UserLogin,
        db: Session = Depends(get_db)
    ):
        """
        Authenticate admin user and return access token for admin endpoints
        """
        try:
            logger.info(f"Admin login attempt for user: {user_credentials.login}")

            from models.structures import Utilisateur

            # For admin login endpoint, use 'administrateur' endpoint type
            # but only allow admin users
            logger.info(f"Querying database for user with login: {user_credentials.login}")
            user = db.query(Utilisateur).filter(Utilisateur.login == user_credentials.login).first()

            logger.info(f"User found in DB: {user is not None}")
            if user:
                logger.info(f"User type: {user.type_utilisateur}")
                logger.info(f"User status: {user.statut}")
                logger.info(f"User ID: {user.id}")
                logger.info(f"User login: {user.login}")

            if not user:
                logger.info(f"User with login '{user_credentials.login}' not found in database")
                # Log failed attempt
                log_login_attempt(db, user_credentials.login, "Echouee", endpoint_type="administrateur")

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if user is of admin type
            logger.info(f"Checking if user has admin rights, user type: {user.type_utilisateur}")
            if user.type_utilisateur not in ["super_administrateur", "administrateur"]:
                logger.info(f"User {user.login} has type {user.type_utilisateur} which is not allowed for admin access")
                # Log unauthorized access attempt
                log_unauthorized_access_attempt(
                    db,
                    str(user.id),
                    "administrateur",
                    "utilisateur",
                    compagnie_id=str(user.compagnie_id) if user.compagnie_id else None
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Admin login is for admin users only",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            logger.info(f"Attempting to authenticate user {user_credentials.login} for admin access")
            user_auth_result = authenticate_user(
                db,
                user_credentials.login,
                user_credentials.password,
                endpoint_type="administrateur"
            )

            if not user_auth_result:
                logger.info(f"Authentication failed for user {user_credentials.login} - incorrect password or blocked account")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            logger.info(f"Authentication successful for user {user_credentials.login}")

            user = user_auth_result["user"]

            # Create user response data
            user_data = {
                "id": str(user.id),
                "login": user.login,
                "profil_id": str(user.profil_id) if user.profil_id else None,
                "stations_user": user.stations_user if user.stations_user else []
            }

            return {
                "success": True,
                "data": {
                    "token": user_auth_result["access_token"],
                    "user": user_data
                }
            }
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log any other exceptions that might occur
            logger.error(f"Unexpected error during admin login: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Create the endpoint
create_login_endpoint()


# Request/response models
class ProfilBase(BaseModel):
    code: str
    libelle: str
    description: str
    compagnie_id: str


class ProfilCreate(ProfilBase):
    permissions: List[str] = []


class ProfilUpdate(BaseModel):
    libelle: str
    description: str
    permissions: List[str] = []


class ProfilResponse(BaseModel):
    id: str
    code: str
    libelle: str
    description: str
    statut: str
    compagnie_id: str


class PermissionBase(BaseModel):
    libelle: str
    description: str
    module_id: str


class PermissionCreate(PermissionBase):
    statut: str = "ACTIF"


class PermissionResponse(BaseModel):
    id: str
    libelle: str
    description: str
    module_id: str
    statut: str


class ModuleBase(BaseModel):
    libelle: str
    statut: str = "ACTIF"


class ModuleResponse(BaseModel):
    id: str
    libelle: str
    statut: str


async def get_current_admin_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    """
    Get the current admin user from the token
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"get_current_admin_user called with token: {bool(token)}")
    if not token:
        logger.error("Token is None or empty")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    logger.info(f"Token payload: {payload}")
    if not payload:
        logger.error("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    logger.info(f"User ID from token: {user_id}")
    if not user_id:
        logger.error("No user ID in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, user_id)
    logger.info(f"User found in DB: {user is not None}")
    if user:
        logger.info(f"User type: {user.type_utilisateur if hasattr(user, 'type_utilisateur') else 'No type_utilisateur field'}")

    is_admin = is_admin_or_super_admin(token)  # Pass the raw token, not the payload
    logger.info(f"Is admin check result: {is_admin}")

    if not user or not is_admin:
        logger.error(f"Access denied - User exists: {user is not None}, Is admin: {is_admin}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("Admin user validation successful")
    return user


@router.get("/profils", response_model=List[ProfilResponse])
async def get_admin_profils(
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all profiles (admin only)
    """
    profils = get_all_profils(db)
    
    return [
        ProfilResponse(
            id=str(profil.id),
            code=profil.code,
            libelle=profil.libelle,
            description=profil.description or "",
            statut=profil.statut,
            compagnie_id=str(profil.compagnie_id) if profil.compagnie_id else ""
        )
        for profil in profils
    ]


@router.post("/profils", response_model=ProfilResponse)
async def create_admin_profil(
    profil_data: ProfilCreate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new profile (admin only)
    """
    try:
        # Validate permissions exist
        for perm_id in profil_data.permissions:
            perm = db.query(Permission).filter(Permission.id == perm_id).first()
            if not perm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission with ID {perm_id} not found"
                )
        
        new_profil = create_profil(
            db,
            code=profil_data.code,
            libelle=profil_data.libelle,
            description=profil_data.description,
            compagnie_id=profil_data.compagnie_id
        )
        
        # Assign permissions to the new profile
        if profil_data.permissions:
            assign_permissions_to_profil(db, str(new_profil.id), profil_data.permissions)
            # Refresh the profile to get updated permissions
            new_profil = db.query(Profil).filter(Profil.id == new_profil.id).first()
        
        return ProfilResponse(
            id=str(new_profil.id),
            code=new_profil.code,
            libelle=new_profil.libelle,
            description=new_profil.description or "",
            statut=new_profil.statut,
            compagnie_id=str(new_profil.compagnie_id) if new_profil.compagnie_id else ""
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/profils/{profil_id}", response_model=ProfilResponse)
async def update_admin_profil(
    profil_id: str,
    profil_data: ProfilUpdate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing profile (admin only)
    """
    from models.structures import Permission  # Import here to avoid circular import
    
    # Validate permissions exist
    for perm_id in profil_data.permissions:
        perm = db.query(Permission).filter(Permission.id == perm_id).first()
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission with ID {perm_id} not found"
            )
    
    updated_profil = update_profil(
        db,
        profil_id,
        libelle=profil_data.libelle,
        description=profil_data.description
    )
    
    if not updated_profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update permissions for the profile
    assign_permissions_to_profil(db, profil_id, profil_data.permissions)
    
    # Refresh the profile to get updated permissions
    updated_profil = db.query(Profil).filter(Profil.id == profil_id).first()
    
    return ProfilResponse(
        id=str(updated_profil.id),
        code=updated_profil.code,
        libelle=updated_profil.libelle,
        description=updated_profil.description or "",
        statut=updated_profil.statut,
        compagnie_id=str(updated_profil.compagnie_id) if updated_profil.compagnie_id else ""
    )


@router.delete("/profils/{profil_id}")
async def delete_admin_profil(
    profil_id: str,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete an existing profile (admin only)
    """
    success = delete_profil(db, profil_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {"success": True, "message": "Profil supprimé avec succès"}


# Models for user management
class UserCreate(BaseModel):
    login: str
    password: str
    nom: str
    profil_id: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    stations_user: List[str] = []
    compagnie_id: Optional[str] = None
    type_utilisateur: str = "utilisateur_compagnie"


class UserUpdate(BaseModel):
    profil_id: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    stations_user: List[str] = []
    statut: Optional[str] = None
    type_utilisateur: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    login: str
    nom: str
    profil_id: Optional[str]
    email: Optional[str]
    telephone: Optional[str]
    stations_user: List[str]
    statut: str
    compagnie_id: Optional[str]
    type_utilisateur: str
    created_at: str
    updated_at: str


@router.get("/users", response_model=List[UserResponse])
async def get_admin_users(
    compagnie_id: Optional[str] = None,
    type_utilisateur: Optional[str] = None,
    statut: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only) - with filters
    """
    users = get_all_users(db, compagnie_id, type_utilisateur, statut, limit, offset)

    return [
        UserResponse(
            id=str(user.id),
            login=user.login,
            nom=user.nom,
            profil_id=str(user.profil_id) if user.profil_id else None,
            email=user.email,
            telephone=user.telephone,
            stations_user=user.stations_user if user.stations_user else [],
            statut=user.statut,
            compagnie_id=str(user.compagnie_id) if user.compagnie_id else None,
            type_utilisateur=user.type_utilisateur,
            created_at=str(user.created_at),
            updated_at=str(user.updated_at)
        )
        for user in users
    ]


@router.post("/users", response_model=UserResponse)
async def create_admin_user(
    user_data: UserCreate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only)
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_login(db, user_data.login)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this login already exists"
            )

        new_user = create_user(
            db,
            login=user_data.login,
            password=user_data.password,
            nom=user_data.nom,
            email=user_data.email,
            telephone=user_data.telephone,
            profil_id=user_data.profil_id,
            compagnie_id=user_data.compagnie_id,
            type_utilisateur=user_data.type_utilisateur
        )

        # Update stations_user if provided
        if user_data.stations_user:
            new_user.stations_user = user_data.stations_user
            db.commit()

        return UserResponse(
            id=str(new_user.id),
            login=new_user.login,
            nom=new_user.nom,
            profil_id=str(new_user.profil_id) if new_user.profil_id else None,
            email=new_user.email,
            telephone=new_user.telephone,
            stations_user=new_user.stations_user if new_user.stations_user else [],
            statut=new_user.statut,
            compagnie_id=str(new_user.compagnie_id) if new_user.compagnie_id else None,
            type_utilisateur=new_user.type_utilisateur,
            created_at=str(new_user.created_at),
            updated_at=str(new_user.updated_at)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_admin_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing user (admin only)
    """
    updated_user = update_user(
        db,
        user_id,
        profil_id=user_data.profil_id,
        email=user_data.email,
        telephone=user_data.telephone,
        stations_user=user_data.stations_user,
        statut=user_data.statut,
        type_utilisateur=user_data.type_utilisateur
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(updated_user.id),
        login=updated_user.login,
        nom=updated_user.nom,
        profil_id=str(updated_user.profil_id) if updated_user.profil_id else None,
        email=updated_user.email,
        telephone=updated_user.telephone,
        stations_user=updated_user.stations_user if updated_user.stations_user else [],
        statut=updated_user.statut,
        compagnie_id=str(updated_user.compagnie_id) if updated_user.compagnie_id else None,
        type_utilisateur=updated_user.type_utilisateur,
        created_at=str(updated_user.created_at),
        updated_at=str(updated_user.updated_at)
    )


@router.delete("/users/{user_id}")
async def delete_admin_user(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete an existing user (admin only)
    """
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"success": True, "message": "User deleted successfully"}


@router.put("/users/{user_id}/activate")
async def activate_admin_user(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate a user (admin only)
    """
    success = activate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"success": True, "message": "User activated successfully"}


@router.put("/users/{user_id}/deactivate")
async def deactivate_admin_user(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user (admin only)
    """
    success = deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"success": True, "message": "User deactivated successfully"}


# Models for company management
class CompanyCreate(BaseModel):
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    pays_id: str
    devise_principale: Optional[str] = "MGA"


class CompanyUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    nif: Optional[str] = None
    pays_id: Optional[str] = None
    devise_principale: Optional[str] = None
    statut: Optional[str] = None


class CompanyResponse(BaseModel):
    id: str
    code: str
    nom: str
    adresse: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    nif: Optional[str]
    statut: str
    pays_id: str
    devise_principale: str
    created_at: str
    updated_at: str


@router.get("/companies", response_model=List[CompanyResponse])
async def get_admin_companies(
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all companies (admin only)
    """
    from models.structures import Compagnie
    companies = db.query(Compagnie).all()

    return [
        CompanyResponse(
            id=str(company.id),
            code=company.code,
            nom=company.nom,
            adresse=company.adresse,
            telephone=company.telephone,
            email=company.email,
            nif=company.nif,
            statut=company.statut,
            pays_id=str(company.pays_id),
            devise_principale=company.devise_principale,
            created_at=str(company.created_at),
            updated_at=str(company.updated_at)
        )
        for company in companies
    ]


@router.post("/companies", response_model=CompanyResponse)
async def create_admin_company(
    company_data: CompanyCreate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new company (admin only)
    """
    from models.structures import Compagnie
    from sqlalchemy.exc import IntegrityError

    # Check if company with this code already exists
    existing_company = db.query(Compagnie).filter(Compagnie.code == company_data.code).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this code already exists"
        )

    try:
        new_company = Compagnie(
            code=company_data.code,
            nom=company_data.nom,
            adresse=company_data.adresse,
            telephone=company_data.telephone,
            email=company_data.email,
            nif=company_data.nif,
            pays_id=company_data.pays_id,
            devise_principale=company_data.devise_principale
        )

        db.add(new_company)
        db.commit()
        db.refresh(new_company)

        return CompanyResponse(
            id=str(new_company.id),
            code=new_company.code,
            nom=new_company.nom,
            adresse=new_company.adresse,
            telephone=new_company.telephone,
            email=new_company.email,
            nif=new_company.nif,
            statut=new_company.statut,
            pays_id=str(new_company.pays_id),
            devise_principale=new_company.devise_principale,
            created_at=str(new_company.created_at),
            updated_at=str(new_company.updated_at)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this code already exists"
        )


# Models for station management
class StationCreate(BaseModel):
    compagnie_id: str
    code: str
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pays_id: str


class StationUpdate(BaseModel):
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
    adresse: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    pays_id: str
    statut: str
    created_at: str


@router.get("/stations", response_model=List[StationResponse])
async def get_admin_stations(
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all stations (admin only)
    """
    from models.structures import Station
    stations = db.query(Station).all()

    return [
        StationResponse(
            id=str(station.id),
            compagnie_id=str(station.compagnie_id),
            code=station.code,
            nom=station.nom,
            adresse=station.adresse,
            telephone=station.telephone,
            email=station.email,
            pays_id=str(station.pays_id),
            statut=station.statut,
            created_at=str(station.created_at)
        )
        for station in stations
    ]


@router.post("/stations", response_model=StationResponse)
async def create_admin_station(
    station_data: StationCreate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new station (admin only)
    """
    from models.structures import Station
    from sqlalchemy.exc import IntegrityError

    # Check if station with this code already exists
    existing_station = db.query(Station).filter(Station.code == station_data.code).first()
    if existing_station:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Station with this code already exists"
        )

    try:
        new_station = Station(
            compagnie_id=station_data.compagnie_id,
            code=station_data.code,
            nom=station_data.nom,
            adresse=station_data.adresse,
            telephone=station_data.telephone,
            email=station_data.email,
            pays_id=station_data.pays_id
        )

        db.add(new_station)
        db.commit()
        db.refresh(new_station)

        return StationResponse(
            id=str(new_station.id),
            compagnie_id=str(new_station.compagnie_id),
            code=new_station.code,
            nom=new_station.nom,
            adresse=new_station.adresse,
            telephone=new_station.telephone,
            email=new_station.email,
            pays_id=str(new_station.pays_id),
            statut=new_station.statut,
            created_at=str(new_station.created_at)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Station with this code already exists"
        )


# Models for country management
class CountryCreate(BaseModel):
    code_pays: str
    nom_pays: str
    devise_principale: Optional[str] = "MGA"
    taux_tva_par_defaut: Optional[float] = 20.0
    systeme_comptable: Optional[str] = "OHADA"
    date_application_tva: Optional[str] = None


class CountryUpdate(BaseModel):
    nom_pays: Optional[str] = None
    devise_principale: Optional[str] = None
    taux_tva_par_defaut: Optional[float] = None
    systeme_comptable: Optional[str] = None
    date_application_tva: Optional[str] = None
    statut: Optional[str] = None


class CountryResponse(BaseModel):
    id: str
    code_pays: str
    nom_pays: str
    devise_principale: str
    taux_tva_par_defaut: float
    systeme_comptable: str
    date_application_tva: Optional[str]
    statut: str
    created_at: str
    updated_at: str


@router.get("/countries", response_model=List[CountryResponse])
async def get_admin_countries(
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all countries (admin only)
    """
    from models.structures import Pays
    countries = db.query(Pays).all()

    return [
        CountryResponse(
            id=str(country.id),
            code_pays=country.code_pays,
            nom_pays=country.nom_pays,
            devise_principale=country.devise_principale,
            taux_tva_par_defaut=float(country.taux_tva_par_defaut) if country.taux_tva_par_defaut else 20.0,
            systeme_comptable=country.systeme_comptable,
            date_application_tva=str(country.date_application_tva) if country.date_application_tva else None,
            statut=country.statut,
            created_at=str(country.created_at),
            updated_at=str(country.updated_at)
        )
        for country in countries
    ]


@router.post("/countries", response_model=CountryResponse)
async def create_admin_country(
    country_data: CountryCreate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new country (admin only)
    """
    from models.structures import Pays
    from sqlalchemy.exc import IntegrityError
    from datetime import datetime

    # Check if country with this code already exists
    existing_country = db.query(Pays).filter(Pays.code_pays == country_data.code_pays).first()
    if existing_country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country with this code already exists"
        )

    # Convert date_application_tva to proper date format if provided
    date_application_tva_converted = None
    if country_data.date_application_tva:
        try:
            # Try to parse the date string to ensure it's in a valid format
            if isinstance(country_data.date_application_tva, str):
                # Parse ISO format date (YYYY-MM-DD)
                date_application_tva_converted = datetime.strptime(country_data.date_application_tva, "%Y-%m-%d").date()
            else:
                date_application_tva_converted = country_data.date_application_tva
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format for date_application_tva. Expected format: YYYY-MM-DD"
            )

    try:
        new_country = Pays(
            code_pays=country_data.code_pays,
            nom_pays=country_data.nom_pays,
            devise_principale=country_data.devise_principale,
            taux_tva_par_defaut=country_data.taux_tva_par_defaut,
            systeme_comptable=country_data.systeme_comptable,
            date_application_tva=date_application_tva_converted
        )

        db.add(new_country)
        db.commit()
        db.refresh(new_country)

        return CountryResponse(
            id=str(new_country.id),
            code_pays=new_country.code_pays,
            nom_pays=new_country.nom_pays,
            devise_principale=new_country.devise_principale,
            taux_tva_par_defaut=float(new_country.taux_tva_par_defaut) if new_country.taux_tva_par_defaut else 20.0,
            systeme_comptable=new_country.systeme_comptable,
            date_application_tva=str(new_country.date_application_tva) if new_country.date_application_tva else None,
            statut=new_country.statut,
            created_at=str(new_country.created_at),
            updated_at=str(new_country.updated_at)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country with this code already exists"
        )


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_admin_permissions(
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all permissions (admin only)
    """
    from models.structures import Permission  # Import here to avoid circular import
    
    permissions = get_all_permissions(db)
    
    return [
        PermissionResponse(
            id=str(perm.id),
            libelle=perm.libelle,
            description=perm.description or "",
            module_id=str(perm.module_id),
            statut=perm.statut
        )
        for perm in permissions
    ]


@router.post("/permissions", response_model=PermissionResponse)
async def create_admin_permission(
    permission_data: PermissionCreate,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new permission (admin only)
    """
    from models.structures import Module  # Import here to avoid circular import
    
    # Verify that the module exists
    module = db.query(Module).filter(Module.id == permission_data.module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with ID {permission_data.module_id} not found"
        )
    
    try:
        new_permission = create_permission(
            db,
            libelle=permission_data.libelle,
            module_id=permission_data.module_id,
            description=permission_data.description,
            statut=permission_data.statut
        )
        
        return PermissionResponse(
            id=str(new_permission.id),
            libelle=new_permission.libelle,
            description=new_permission.description or "",
            module_id=str(new_permission.module_id),
            statut=new_permission.statut
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/modules", response_model=List[ModuleResponse])
async def get_admin_modules(
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all modules (admin only)
    """
    from models.structures import Module  # Import here to avoid circular import
    
    modules = get_all_modules(db)
    
    return [
        ModuleResponse(
            id=str(module.id),
            libelle=module.libelle,
            statut=module.statut
        )
        for module in modules
    ]


@router.post("/modules", response_model=ModuleResponse)
async def create_admin_module(
    module_data: ModuleBase,
    current_user: Utilisateur = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new module (admin only)
    """
    try:
        new_module = create_module(
            db,
            libelle=module_data.libelle,
            statut=module_data.statut
        )
        
        return ModuleResponse(
            id=str(new_module.id),
            libelle=new_module.libelle,
            statut=new_module.statut
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )