from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.database import get_db
from models.structures import Profil, Permission, Module, Utilisateur
from services.rbac_service import (
    create_profil, get_profil_by_id, update_profil, delete_profil,
    get_all_profils, get_all_permissions, get_all_modules,
    create_permission, create_module, get_permissions_for_profil,
    assign_permissions_to_profil, get_permission_by_id, get_module_by_id
)
from services.auth_service import get_user_by_id, create_user, update_user
from utils.security import verify_token
from utils.dependencies import get_current_user
import uuid


# Create API router
router = APIRouter(
    tags=["rbac"],
    responses={404: {"description": "Endpoint non trouvé"}}
)


# Request/response models
from pydantic import BaseModel


class ProfilBase(BaseModel):
    code: str
    libelle: str
    description: str
    compagnie_id: str
    type_profil: str = "utilisateur_compagnie"


class ProfilCreate(ProfilBase):
    permissions: List[str] = []


class ProfilUpdate(BaseModel):
    libelle: Optional[str] = None
    description: Optional[str] = None
    type_profil: Optional[str] = None
    statut: Optional[str] = None
    permissions: List[str] = []


class ProfilResponse(BaseModel):
    id: str
    code: str
    libelle: str
    description: str
    compagnie_id: str
    type_profil: str
    statut: str
    created_at: str
    updated_at: Optional[str] = None
    permissions: Optional[List[dict]] = []

    class Config:
        from_attributes = True


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
    created_at: str

    class Config:
        from_attributes = True


class ModuleBase(BaseModel):
    libelle: str
    statut: str = "ACTIF"


class ModuleResponse(BaseModel):
    id: str
    libelle: str
    statut: str

    class Config:
        from_attributes = True


class CheckPermissionRequest(BaseModel):
    user_id: str
    permission: str


class CheckPermissionResponse(BaseModel):
    has_permission: bool


class UserPermissionsResponse(BaseModel):
    user_id: str
    profil: Optional[ProfilResponse] = None
    permissions: List[PermissionResponse]


class PaginationResponse(BaseModel):
    total: int
    limit: int
    offset: int


class ProfilListResponse(BaseModel):
    success: bool
    data: List[ProfilResponse]
    pagination: PaginationResponse


class UserBase(BaseModel):
    login: str
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    profil_id: Optional[str] = None
    compagnie_id: Optional[str] = None
    type_utilisateur: str = "utilisateur_compagnie"
    stations_user: List[str] = []


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    profil_id: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    stations_user: Optional[List[str]] = None
    statut: Optional[str] = None
    type_utilisateur: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    login: str
    nom: str
    profil_id: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    stations_user: List[str]
    statut: str
    compagnie_id: str
    type_utilisateur: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    success: bool
    data: List[UserResponse]
    pagination: PaginationResponse




@router.get("/profiles", response_model=ProfilListResponse)
async def get_profiles(
    compagnie_id: Optional[str] = Query(None, description="Filter by company ID"),
    statut: Optional[str] = Query(None, description="Filter by status ('Actif', 'Inactif', 'Supprime')"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lister les profils d'une compagnie with optional filters
    """
    profils = get_all_profils(db)

    # Apply filters
    if compagnie_id:
        profils = [p for p in profils if str(p.compagnie_id) == compagnie_id]

    if statut:
        profils = [p for p in profils if p.statut == statut]

    total = len(profils)

    # Apply pagination
    paginated_profils = profils[offset:offset+limit]

    result = []
    for profil in paginated_profils:
        # Get permissions for the profile
        permissions = get_permissions_for_profil(db, str(profil.id))

        profil_response = ProfilResponse(
            id=str(profil.id),
            code=profil.code,
            libelle=profil.libelle,
            description=profil.description or "",
            compagnie_id=str(profil.compagnie_id) if profil.compagnie_id else "",
            type_profil=profil.type_profil,
            statut=profil.statut,
            created_at=profil.created_at.isoformat(),
            updated_at=profil.updated_at.isoformat() if profil.updated_at else None,
            permissions=[
                {
                    "id": str(perm.id),
                    "libelle": perm.libelle,
                    "module_id": str(perm.module_id)
                }
                for perm in permissions
            ] if permissions else []
        )
        result.append(profil_response)

    return ProfilListResponse(
        success=True,
        data=result,
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.get("/profiles/{profile_id}", response_model=ProfilResponse)
async def get_profile_by_id(
    profile_id: str,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer les détails d'un profil avec ses permissions
    """
    profil = get_profil_by_id(db, profile_id)
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Get permissions for the profile
    permissions = get_permissions_for_profil(db, profile_id)

    return ProfilResponse(
        id=str(profil.id),
        code=profil.code,
        libelle=profil.libelle,
        description=profil.description or "",
        compagnie_id=str(profil.compagnie_id) if profil.compagnie_id else "",
        type_profil=profil.type_profil,
        statut=profil.statut,
        created_at=profil.created_at.isoformat(),
        updated_at=profil.updated_at.isoformat() if profil.updated_at else None,
        permissions=[
            {
                "id": str(perm.id),
                "libelle": perm.libelle,
                "module_id": str(perm.module_id)
            }
            for perm in permissions
        ] if permissions else []
    )


@router.post("/profiles", response_model=ProfilResponse)
async def create_new_profile(
    profil_data: ProfilCreate,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer un nouveau profil
    """
    try:
        # Validate permissions exist
        for perm_id in profil_data.permissions:
            perm = get_permission_by_id(db, perm_id)
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
            compagnie_id=profil_data.compagnie_id,
            type_profil=profil_data.type_profil  # Adding the type_profil
        )

        # Assign permissions to the new profile
        if profil_data.permissions:
            assign_permissions_to_profil(db, str(new_profil.id), profil_data.permissions)
            # Refresh the profile to get updated permissions
            new_profil = get_profil_by_id(db, str(new_profil.id))

        # Get updated permissions
        permissions = get_permissions_for_profil(db, str(new_profil.id))

        return ProfilResponse(
            id=str(new_profil.id),
            code=new_profil.code,
            libelle=new_profil.libelle,
            description=new_profil.description or "",
            compagnie_id=str(new_profil.compagnie_id) if new_profil.compagnie_id else "",
            type_profil=new_profil.type_profil,  # Adding the type_profil to response
            statut=new_profil.statut,
            created_at=new_profil.created_at.isoformat(),
            updated_at=new_profil.updated_at.isoformat() if new_profil.updated_at else None,
            permissions=[
                {
                    "id": str(perm.id),
                    "libelle": perm.libelle,
                    "module_id": str(perm.module_id)
                }
                for perm in permissions
            ] if permissions else []
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/profiles/{profile_id}", response_model=ProfilResponse)
async def update_existing_profile(
    profile_id: str,
    profil_data: ProfilUpdate,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour un profil
    """
    # Validate permissions exist
    for perm_id in profil_data.permissions:
        perm = get_permission_by_id(db, perm_id)
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission with ID {perm_id} not found"
            )

    updated_profil = update_profil(
        db,
        profile_id,
        libelle=profil_data.libelle,
        description=profil_data.description,
        type_profil=profil_data.type_profil,  # Updating type_profil
        statut=profil_data.statut
    )

    if not updated_profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Update permissions for the profile
    assign_permissions_to_profil(db, profile_id, profil_data.permissions)

    # Refresh the profile to get updated permissions
    updated_profil = get_profil_by_id(db, profile_id)

    # Get updated permissions
    permissions = get_permissions_for_profil(db, profile_id)

    return ProfilResponse(
        id=str(updated_profil.id),
        code=updated_profil.code,
        libelle=updated_profil.libelle,
        description=updated_profil.description or "",
        compagnie_id=str(updated_profil.compagnie_id) if updated_profil.compagnie_id else "",
        type_profil=updated_profil.type_profil,  # Including type_profil in response
        statut=updated_profil.statut,
        created_at=updated_profil.created_at.isoformat(),
        updated_at=updated_profil.updated_at.isoformat() if updated_profil.updated_at else None,
        permissions=[
            {
                "id": str(perm.id),
                "libelle": perm.libelle,
                "module_id": str(perm.module_id)
            }
            for perm in permissions
        ] if permissions else []
    )


@router.get("/users", response_model=UserListResponse)
async def get_users_list(
    compagnie_id: Optional[str] = Query(None, description="Filter by company ID"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    type_utilisateur: Optional[str] = Query(None, description="Filter by user type"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lister les utilisateurs d'une compagnie
    """
    from sqlalchemy import and_
    from utils.access_control import is_admin_or_super_admin

    query = db.query(Utilisateur)

    # Apply filtering based on user type
    user_type = current_user.type_utilisateur
    if not is_admin_or_super_admin(user_type):
        # Non-admin users can only see users from their own company
        if current_user.compagnie_id:
            query = query.filter(Utilisateur.compagnie_id == current_user.compagnie_id)
        else:
            # If user doesn't have a company (should not happen for non-admins), return empty list
            query = query.filter(Utilisateur.id == '00000000-0000-0000-0000-000000000000')  # No results

    # Additional filters can still be applied by admins
    if compagnie_id and is_admin_or_super_admin(user_type):
        query = query.filter(Utilisateur.compagnie_id == compagnie_id)

    if statut:
        query = query.filter(Utilisateur.statut == statut)

    if type_utilisateur:
        query = query.filter(Utilisateur.type_utilisateur == type_utilisateur)

    users = query.offset(offset).limit(limit).all()
    total = query.count()

    return UserListResponse(
        success=True,
        data=[
            UserResponse(
                id=str(user.id),
                login=user.login,
                nom=user.nom,
                profil_id=str(user.profil_id) if user.profil_id else None,
                email=user.email,
                telephone=user.telephone,
                stations_user=user.stations_user if user.stations_user else [],
                statut=user.statut,
                compagnie_id=str(user.compagnie_id) if user.compagnie_id else "",
                type_utilisateur=user.type_utilisateur,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat() if user.updated_at else None
            )
            for user in users
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )


@router.post("/users", response_model=UserResponse)
async def create_new_user(
    user_data: UserCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer un nouvel utilisateur
    """
    try:
        db_user = create_user(
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

        return UserResponse(
            id=str(db_user.id),
            login=db_user.login,
            nom=db_user.nom,
            profil_id=str(db_user.profil_id) if db_user.profil_id else None,
            email=db_user.email,
            telephone=db_user.telephone,
            stations_user=db_user.stations_user if db_user.stations_user else [],
            statut=db_user.statut,
            compagnie_id=str(db_user.compagnie_id) if db_user.compagnie_id else "",
            type_utilisateur=db_user.type_utilisateur,
            created_at=db_user.created_at.isoformat(),
            updated_at=db_user.updated_at.isoformat() if db_user.updated_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_existing_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour un utilisateur
    """
    updated_user = update_user(db, user_id, **user_data.dict(exclude_unset=True))
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
        compagnie_id=str(updated_user.compagnie_id) if updated_user.compagnie_id else "",
        type_utilisateur=updated_user.type_utilisateur,
        created_at=updated_user.created_at.isoformat(),
        updated_at=updated_user.updated_at.isoformat() if updated_user.updated_at else None
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id_endpoint(
    user_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer les détails d'un utilisateur
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(user.id),
        login=user.login,
        nom=user.nom,
        profil_id=str(user.profil_id) if user.profil_id else None,
        email=user.email,
        telephone=user.telephone,
        stations_user=user.stations_user if user.stations_user else [],
        statut=user.statut,
        compagnie_id=str(user.compagnie_id) if user.compagnie_id else "",
        type_utilisateur=user.type_utilisateur,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat() if user.updated_at else None
    )


@router.get("/profils", response_model=List[ProfilResponse])
async def get_profils(
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all profiles (legacy endpoint)
    """
    profils = get_all_profils(db)

    return [
        ProfilResponse(
            id=str(profil.id),
            code=profil.code,
            libelle=profil.libelle,
            description=profil.description or "",
            compagnie_id=str(profil.compagnie_id) if profil.compagnie_id else "",
            type_profil=profil.type_profil,
            statut=profil.statut,
            created_at=profil.created_at.isoformat(),
            updated_at=profil.updated_at.isoformat() if profil.updated_at else None,
            permissions=[]
        )
        for profil in profils
    ]


@router.post("/modules", response_model=ModuleResponse)
async def create_new_module(
    module_data: ModuleBase,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new module
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


@router.get("/modules", response_model=List[ModuleResponse])
async def get_modules(
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all modules
    """
    modules = get_all_modules(db)

    return [
        ModuleResponse(
            id=str(module.id),
            libelle=module.libelle,
            statut=module.statut
        )
        for module in modules
    ]


@router.post("/permissions", response_model=PermissionResponse)
async def create_new_permission(
    permission_data: PermissionCreate,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new permission
    """
    # Verify that the module exists
    module = get_module_by_id(db, permission_data.module_id)
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
            statut=new_permission.statut,
            created_at=new_permission.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all permissions
    """
    permissions = get_all_permissions(db)

    return [
        PermissionResponse(
            id=str(perm.id),
            libelle=perm.libelle,
            description=perm.description or "",
            module_id=str(perm.module_id),
            statut=perm.statut,
            created_at=perm.created_at.isoformat()
        )
        for perm in permissions
    ]


@router.get("/access-control/user-permissions/{user_id}", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: str,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all permissions for a specific user
    """
    from services.rbac_service import get_permissions_for_user

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    permissions = get_permissions_for_user(db, user_id)
    profil = get_profil_by_id(db, str(user.profil_id)) if user.profil_id else None

    profil_data = None
    if profil:
        profil_data = ProfilResponse(
            id=str(profil.id),
            code=profil.code,
            libelle=profil.libelle,
            description=profil.description or "",
            compagnie_id=str(profil.compagnie_id) if profil.compagnie_id else "",
            statut=profil.statut,
            created_at=profil.created_at.isoformat(),
            updated_at=profil.updated_at.isoformat() if profil.updated_at else None,
            permissions=[]
        )

    permissions_data = [
        PermissionResponse(
            id=str(perm.id),
            libelle=perm.libelle,
            description=perm.description or "",
            module_id=str(perm.module_id),
            statut=perm.statut,
            created_at=perm.created_at.isoformat()
        )
        for perm in permissions
    ]

    return UserPermissionsResponse(
        user_id=user_id,
        profil=profil_data,
        permissions=permissions_data
    )


@router.post("/access-control/check-permission", response_model=CheckPermissionResponse)
async def check_user_permission_endpoint(
    request: CheckPermissionRequest,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a user has a specific permission
    """
    from services.rbac_service import check_user_permission

    has_permission = check_user_permission(db, request.user_id, request.permission)
    return CheckPermissionResponse(has_permission=has_permission)


