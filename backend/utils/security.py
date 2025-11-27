import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from config.config import settings
from models.structures import Utilisateur


def hash_password(password: str) -> str:
    """
    Hash a password with bcrypt
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to 10 hours if not specified
        expire = datetime.utcnow() + timedelta(hours=10)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.exceptions.PyJWTError:
        return None


def get_user_type_from_token(token: str) -> Optional[str]:
    """
    Extract the user type from a JWT token
    """
    payload = verify_token(token)
    if payload:
        return payload.get("type_utilisateur")
    return None


def is_admin_user_type(user_type: str) -> bool:
    """
    Check if the user type is an admin type
    """
    return user_type in ["super_administrateur", "administrateur"]


def is_user_endpoint_token(token: str) -> bool:
    """
    Check if the token is valid for the user endpoint
    """
    payload = verify_token(token)
    if payload:
        user_type = payload.get("type_utilisateur")
        token_endpoint_type = payload.get("type_endpoint", "utilisateur")
        
        # Admin types should use admin endpoint
        if is_admin_user_type(user_type):
            return token_endpoint_type == "administrateur"
        # Regular users should use user endpoint
        else:
            return token_endpoint_type == "utilisateur"
    
    return False


def is_admin_endpoint_token(token: str) -> bool:
    """
    Check if the token is valid for the admin endpoint
    """
    payload = verify_token(token)
    if payload:
        user_type = payload.get("type_utilisateur")
        token_endpoint_type = payload.get("type_endpoint", "utilisateur")
        
        # Only admin types can access admin endpoint
        if is_admin_user_type(user_type):
            return token_endpoint_type == "administrateur"
        else:
            # Non-admin users cannot access admin endpoint
            return False
    
    return False