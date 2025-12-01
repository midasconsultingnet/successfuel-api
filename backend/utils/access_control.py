import inspect
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from typing import Callable, Optional
from functools import wraps
from database.database import get_db
from models.structures import Utilisateur
from services.auth_service import get_user_by_id
from services.rbac_service import check_user_permission
from utils.security import verify_token, is_admin_endpoint_token, is_user_endpoint_token
import uuid


async def get_current_user_from_token(
    request: Request,
    db: Session = Depends(get_db)
) -> Utilisateur:
    """
    Dependency to extract the current user from JWT token
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or not Bearer token"
        )

    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    current_user = get_user_by_id(db, user_id)
    if not current_user or current_user.statut != "Actif":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return current_user


def create_permission_dependency(permission: str):
    """
    Creates a FastAPI dependency for checking permissions
    Designed to be used with FastAPI's Depends()
    """
    async def permission_dependency(
        request: Request,
        db: Session = Depends(get_db)
    ) -> Utilisateur:
        # Extract and validate the token from the request
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing or not Bearer token"
            )

        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        current_user = get_user_by_id(db, user_id)
        if not current_user or current_user.statut != "Actif":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Check if the user is a 'gerant_compagnie', if so they have all permissions for their company
        has_perm = False
        if current_user.type_utilisateur == "gerant_compagnie":
            # Gérant de compagnie has all permissions for their own company
            has_perm = True
        else:
            # For other user types, check the specific permission
            has_perm = check_user_permission(db, current_user.id, permission)

        if not has_perm:
            # Log the permission failure
            from services.security_service import log_security_event
            log_security_event(
                db,
                type_evenement="tentative_acces_non_autorise",
                utilisateur_id=str(current_user.id),
                description=f"Tentative d'accéder à {permission} sans autorisation",
                compagnie_id=str(current_user.compagnie_id) if current_user.compagnie_id else None
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )

        return current_user
    return permission_dependency


def require_permission(permission: str):
    """
    Decorator to check if a user has a specific permission
    This can be used as a decorator or as a dependency function
    """
    def permission_checker(func):
        # For now, we just return the function as is to maintain compatibility
        # The permission checking will be done inside the function itself
        return func
    return permission_checker


def get_require_permission_dependency(permission: str):
    """
    Alias for require_permission to provide backward compatibility
    """
    return create_permission_dependency(permission)


def require_user_access(stations_check: bool = True):
    """
    Decorator to ensure the endpoint is accessed by a user endpoint token
    """
    def access_checker(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = kwargs.get('token') or next((arg for arg in args if isinstance(arg, str)), None)
            
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token not provided"
                )
            
            # Check if the token is valid for user endpoint
            if not is_user_endpoint_token(token):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: This endpoint is restricted to user tokens"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return access_checker


def require_admin_access(stations_check: bool = True):
    """
    Decorator to ensure the endpoint is accessed by an admin endpoint token
    """
    def access_checker(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = kwargs.get('token') or next((arg for arg in args if isinstance(arg, str)), None)
            
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token not provided"
                )
            
            # Check if the token is valid for admin endpoint
            if not is_admin_endpoint_token(token):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: This endpoint is restricted to admin tokens"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return access_checker


def check_station_access(user_stations: list, requested_station_id: str) -> bool:
    """
    Check if a user has access to a specific station
    """
    if not user_stations:
        return False

    # If the user has access to all stations (represented by an empty list or a wildcard)
    # In SuccessFuel, an empty list might mean access to all stations
    if len(user_stations) == 0 or '*' in user_stations:
        return True

    # Check if the requested station is in the user's allowed stations
    return requested_station_id in user_stations


def check_user_station_access(user: Utilisateur, requested_station_id: str) -> bool:
    """
    Check if a user has access to a specific station based on their stations_user field
    """
    user_stations = user.stations_user or []
    return check_station_access(user_stations, requested_station_id)


def require_station_access(station_id_param: str = "station_id"):
    """
    Decorator to check if a user has access to a specific station
    """
    def station_checker(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the database session and token from the function arguments
            db = kwargs.get('db')
            token = kwargs.get('token')  # This is from get_token_from_header dependency

            # Check if current_user is available (which means token was already validated)
            current_user = kwargs.get('current_user')

            if not db:
                # Look for db in args as a fallback
                db = next((arg for arg in args if isinstance(arg, Session)), None)

            if not token and not current_user:
                # Look for token in args as a fallback
                token = next((arg for arg in args if isinstance(arg, str) and len(arg) > 10), None)

            # If we have current_user, we can proceed - token was already validated
            user = current_user if current_user else None

            # If we still don't have db or token/current_user, raise error
            if not db and not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Database session or token not provided"
                )

            # If we don't have the current_user, we need to validate the token
            if not user:
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token not provided"
                    )

                # Verify the token and get user info
                payload = verify_token(token)
                if not payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )

                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials"
                    )

                # Get user from database
                user = get_user_by_id(db, user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )

            # Get the station ID from parameters
            station_id = kwargs.get(station_id_param)
            if not station_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Station ID parameter '{station_id_param}' not provided"
                )

            # If user is a 'gerant_compagnie', check if the station belongs to their company
            # They have access to all stations in their company
            if user.type_utilisateur == "gerant_compagnie":
                from models.structures import Station
                station = db.query(Station).filter(Station.id == station_id).first()
                if not station or str(station.compagnie_id) != str(user.compagnie_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied: Station does not belong to your company"
                    )
            else:
                # For other user types, check first if the station belongs to their company
                from models.structures import Station
                station = db.query(Station).filter(Station.id == station_id).first()
                if not station or str(station.compagnie_id) != str(user.compagnie_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied: Station does not belong to your company"
                    )

                # Then check if they have specific access to this station via stations_user field
                if not check_user_station_access(user, station_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied: You don't have access to station {station_id}"
                    )

            return await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)
        return wrapper
    return station_checker


def check_company_access(user: Utilisateur, target_company_id: str) -> bool:
    """
    Check if a user has access to data from a specific company.
    Gérants de compagnie can only access data from their own company.
    """
    if user.type_utilisateur == "gerant_compagnie":
        # Gérant de compagnie can only access data from their own company
        return str(user.compagnie_id) == str(target_company_id)
    else:
        # Other user types follow the standard permission system
        return True


def require_company_access(company_id_param: str = "company_id"):
    """
    Decorator to check if a user has access to a specific company's data
    """
    def company_checker(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the database session and token from the function arguments
            db = kwargs.get('db')
            token = kwargs.get('token')  # This is from get_token_from_header dependency

            # Check if current_user is available (which means token was already validated)
            current_user = kwargs.get('current_user')

            if not db:
                # Look for db in args as a fallback
                db = next((arg for arg in args if isinstance(arg, Session)), None)

            if not token and not current_user:
                # Look for token in args as a fallback
                token = next((arg for arg in args if isinstance(arg, str) and len(arg) > 10), None)

            # If we have current_user, we can proceed - token was already validated
            user = current_user if current_user else None

            # If we still don't have db or token/current_user, raise error
            if not db and not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Database session or token not provided"
                )

            # If we don't have the current_user, we need to validate the token
            if not user:
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token not provided"
                    )

                # Verify the token and get user info
                payload = verify_token(token)
                if not payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )

                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials"
                    )

                # Get user from database
                user = get_user_by_id(db, user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )

            # Get the company ID from parameters
            company_id = kwargs.get(company_id_param)
            if not company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Company ID parameter '{company_id_param}' not provided"
                )

            # Check if user has access to the requested company
            if not check_company_access(user, company_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: You don't have access to data from company {company_id}"
                )

            return await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)
        return wrapper
    return company_checker


# Helper functions for access control
def check_user_type_access(token: str, allowed_types: list) -> bool:
    """
    Check if the user type in the token is in the allowed types
    """
    payload = verify_token(token)
    if not payload:
        return False

    user_type = payload.get("type_utilisateur")
    return user_type in allowed_types


def is_super_admin(token: str) -> bool:
    """
    Check if the user is a super admin
    """
    payload = verify_token(token)
    if not payload:
        return False

    user_type = payload.get("type_utilisateur")
    return user_type == "super_administrateur"


def is_admin_or_super_admin(token: str) -> bool:
    """
    Check if the user is an admin or super admin
    """
    payload = verify_token(token)
    if not payload:
        return False

    user_type = payload.get("type_utilisateur")
    return user_type in ["super_administrateur", "administrateur"]


def is_gerant_compagnie(user_type: str) -> bool:
    """
    Check if the user is a gérant de compagnie
    """
    return user_type == "gerant_compagnie"


def is_utilisateur_compagnie(user_type: str) -> bool:
    """
    Check if the user is an utilisateur de compagnie
    """
    return user_type == "utilisateur_compagnie"


def has_permission(db: Session, user_id: str, permission: str) -> bool:
    """
    Check if a user has a specific permission
    """
    from services.rbac_service import check_user_permission
    # Check if user is a 'gerant_compagnie', if so they have all permissions for their company
    user = get_user_by_id(db, user_id)
    if user and user.type_utilisateur == "gerant_compagnie":
        # Gérant de compagnie has all permissions for their own company
        return True
    else:
        return check_user_permission(db, user_id, permission)


def verify_entity_access(db: Session, user: Utilisateur, entity: any, entity_name: str = "entity") -> bool:
    """
    Verify that a user has access to a specific entity based on company ownership
    """
    from utils.access_control import is_admin_or_super_admin

    # Admins and super admins can access any entity
    user_type = user.type_utilisateur
    if is_admin_or_super_admin(user_type):
        return True

    # Check if entity has a compagnie_id attribute
    if not hasattr(entity, 'compagnie_id'):
        # If the entity doesn't have a compagnie_id, we can't check company access
        return True

    # For gérants and other users, verify that the entity belongs to their company
    entity_company_id = str(entity.compagnie_id) if entity.compagnie_id else None
    user_company_id = str(user.compagnie_id) if user.compagnie_id else None

    if entity_company_id != user_company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access to {entity_name} not authorized for this user's company"
        )

    return True




def prohibit_super_admin_access(func: Callable):
    """
    Decorator to prevent super administrators from accessing daily operations
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract token from kwargs or args
        token = kwargs.get('token') or next((arg for arg in args if isinstance(arg, str) and len(arg) > 10), None)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not provided"
            )

        # Check if the user is a super admin
        if is_super_admin(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super administrators are not allowed to perform daily operations"
            )

        # If not a super admin, proceed with the original function
        return await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

    return wrapper