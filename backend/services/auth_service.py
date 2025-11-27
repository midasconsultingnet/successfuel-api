from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.structures import Utilisateur
from models.securite import AuthToken, TentativeConnexion, TentativeAccesNonAutorise
from utils.security import hash_password, verify_password, create_access_token
from config.config import settings
import uuid


def authenticate_user(db: Session, login: str, password: str, endpoint_type: str = "utilisateur") -> Optional[dict]:
    """
    Authenticate a user by login and password
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"authenticate_user called for login: {login}, endpoint_type: {endpoint_type}")

    try:
        # Find the user by login
        user = db.query(Utilisateur).filter(Utilisateur.login == login).first()

        if not user:
            logger.info(f"User with login '{login}' not found in database")
            # Log failed attempt
            log_login_attempt(db, login, "Echouee", endpoint_type=endpoint_type)
            return None

        logger.info(f"User found: {user.login}, type: {user.type_utilisateur}, status: {user.statut}")

        if not verify_password(password, user.mot_de_passe):
            logger.info(f"Password verification failed for user: {login}")
            # Log failed attempt
            log_login_attempt(db, login, "Echouee", endpoint_type=endpoint_type)
            return None

        logger.info(f"Password verification succeeded for user: {login}")

        if user.statut in ["Inactif", "Supprime", "Bloque"]:
            logger.info(f"User {login} has status {user.statut} which prevents login")
            # Log blocked account attempt
            log_login_attempt(db, login, "Echouee", user_id=user.id, endpoint_type=endpoint_type,
                             type_utilisateur=user.type_utilisateur)
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        logger.info(f"Updated last login for user: {login}")

        # Log successful attempt
        log_login_attempt(db, login, "Reussie", user_id=user.id, endpoint_type=endpoint_type,
                         type_utilisateur=user.type_utilisateur)

        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

        # Include user type and endpoint type in token payload
        token_data = {
            "sub": str(user.id),
            "login": user.login,
            "type_utilisateur": user.type_utilisateur,
            "type_endpoint": endpoint_type
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )

        logger.info(f"Successfully created access token for user: {login}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except Exception as e:
        logger.error(f"Unexpected error during authentication for user {login}: {str(e)}", exc_info=True)
        return None


def create_user(db: Session, login: str, password: str, nom: str, email: Optional[str] = None, 
                telephone: Optional[str] = None, profil_id: Optional[str] = None, 
                compagnie_id: Optional[str] = None, type_utilisateur: str = "utilisateur_compagnie") -> Utilisateur:
    """
    Create a new user with hashed password
    """
    # Check if login already exists
    existing_user = db.query(Utilisateur).filter(Utilisateur.login == login).first()
    if existing_user:
        raise ValueError("Login already exists")
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create new user
    db_user = Utilisateur(
        login=login,
        mot_de_passe=hashed_password,
        nom=nom,
        email=email,
        telephone=telephone,
        profil_id=profil_id,
        compagnie_id=compagnie_id,
        type_utilisateur=type_utilisateur
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user_by_id(db: Session, user_id: str) -> Optional[Utilisateur]:
    """
    Get a user by ID
    """
    return db.query(Utilisateur).filter(Utilisateur.id == user_id).first()


def get_user_by_login(db: Session, login: str) -> Optional[Utilisateur]:
    """
    Get a user by login
    """
    return db.query(Utilisateur).filter(Utilisateur.login == login).first()


def update_user(db: Session, user_id: str, **kwargs) -> Optional[Utilisateur]:
    """
    Update user information
    """
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            if key == 'mot_de_passe' and value:  # Only hash if password is being updated
                value = hash_password(value)
            setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user


def delete_user(db: Session, user_id: str) -> bool:
    """
    Logically delete a user (set status to 'Supprime')
    """
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        return False
    
    user.statut = "Supprime"
    db.commit()
    return True


def activate_user(db: Session, user_id: str) -> bool:
    """
    Activate a user
    """
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        return False
    
    user.statut = "Actif"
    db.commit()
    return True


def deactivate_user(db: Session, user_id: str) -> bool:
    """
    Deactivate a user
    """
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        return False
    
    user.statut = "Inactif"
    db.commit()
    return True


def log_login_attempt(db: Session, login: str, result: str, user_id: Optional[str] = None, 
                      ip_address: Optional[str] = None, endpoint_type: str = "utilisateur", 
                      type_utilisateur: str = "utilisateur_compagnie"):
    """
    Log a login attempt (successful or failed)
    """
    attempt = TentativeConnexion(
        login=login,
        ip_connexion=ip_address,
        resultat_connexion=result,
        utilisateur_id=user_id,
        type_endpoint=endpoint_type,
        type_utilisateur=type_utilisateur,
        created_at=datetime.utcnow()
    )
    
    db.add(attempt)
    db.commit()


def log_unauthorized_access_attempt(db: Session, user_id: str, accessed_endpoint: str, 
                                   authorized_endpoint: str, ip_address: Optional[str] = None,
                                   compagnie_id: Optional[str] = None):
    """
    Log an unauthorized access attempt to an endpoint
    """
    attempt = TentativeAccesNonAutorise(
        utilisateur_id=user_id,
        endpoint_accesse=accessed_endpoint,
        endpoint_autorise=authorized_endpoint,
        ip_connexion=ip_address,
        compagnie_id=compagnie_id,
        created_at=datetime.utcnow()
    )
    
    db.add(attempt)
    db.commit()


def create_refresh_token(db: Session, user_id: str, endpoint_type: str = "utilisateur") -> str:
    """
    Create a refresh token for the user
    """
    # In a real implementation, you would store refresh tokens in the database
    # and provide methods to validate and rotate them
    # For now, we just return a token
    
    refresh_token_expires = timedelta(days=7)  # Refresh tokens valid for 7 days
    
    token_data = {
        "sub": str(user_id),
        "type": "refresh",
        "type_endpoint": endpoint_type
    }
    
    refresh_token = create_access_token(
        data=token_data,
        expires_delta=refresh_token_expires
    )
    
    return refresh_token


def logout_user(db: Session, token: str) -> bool:
    """
    Invalidate a user's token (placeholder implementation)
    """
    # In a real implementation, you would store tokens in a blacklist
    # or have a mechanism to invalidate specific tokens
    # For now, we just return success
    return True


def logout_all_user_sessions(db: Session, user_id: str) -> int:
    """
    Invalidate all tokens for a specific user (placeholder implementation)
    """
    # In a real implementation, you would update the auth_tokens table
    # to mark tokens as inactive for this user
    # For now, we just return the count of affected tokens
    return 0


def get_all_users(db: Session, compagnie_id: str = None, type_utilisateur: str = None, statut: str = None, limit: int = 50, offset: int = 0) -> list:
    """
    Get all users with optional filters
    """
    query = db.query(Utilisateur)

    if compagnie_id:
        query = query.filter(Utilisateur.compagnie_id == compagnie_id)

    if type_utilisateur:
        query = query.filter(Utilisateur.type_utilisateur == type_utilisateur)

    if statut:
        query = query.filter(Utilisateur.statut == statut)

    # Order by creation date and apply pagination
    users = query.order_by(Utilisateur.created_at.desc()).offset(offset).limit(limit).all()

    return users