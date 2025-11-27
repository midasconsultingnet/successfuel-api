from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Callable, Optional
from functools import wraps
from database.database import get_db
from models.structures import Utilisateur
from services.auth_service import get_user_by_id
from services.rbac_service import check_user_permission
from utils.security import verify_token, is_admin_endpoint_token, is_user_endpoint_token
import uuid


def require_permission(permission: str):
    """
    Decorator to check if a user has a specific permission
    """
    def permission_checker(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the database session and token from the function arguments
            db = kwargs.get('db') or next((arg for arg in args if isinstance(arg, Session)), None)
            token = kwargs.get('token') or next((arg for arg in args if isinstance(arg, str)), None)
            
            if not db or not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Database session or token not provided"
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
            
            # Check if the user has the required permission
            has_perm = check_user_permission(db, user_id, permission)
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return permission_checker


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


def require_station_access(station_id_param: str = "station_id"):
    """
    Decorator to check if a user has access to a specific station
    """
    def station_checker(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the database session and token from the function arguments
            db = kwargs.get('db') or next((arg for arg in args if isinstance(arg, Session)), None)
            token = kwargs.get('token') or next((arg for arg in args if isinstance(arg, str)), None)
            
            if not db or not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Database session or token not provided"
                )
            
            # Get the station ID from parameters
            station_id = kwargs.get(station_id_param)
            if not station_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Station ID parameter '{station_id_param}' not provided"
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
            
            # Check if user has access to the requested station
            user_stations = user.stations_user or []
            if not check_station_access(user_stations, station_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: You don't have access to station {station_id}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return station_checker


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


def has_permission(db: Session, user_id: str, permission: str) -> bool:
    """
    Check if a user has a specific permission
    """
    from services.rbac_service import check_user_permission
    return check_user_permission(db, user_id, permission)